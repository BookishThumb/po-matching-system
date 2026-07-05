# pyrefly: ignore
# type: ignore
import time
from sqlalchemy.exc import OperationalError
from app.utils.logger import logger
from app.ingestion.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from app.ai.extractor import extract_invoice_data
from app.matching.po_matcher import get_purchase_order, compare_invoice_to_po
from app.matching.discrepancy import detect_discrepancies, Discrepancy
from app.matching.validation_rules import determine_validation_status, summarize_discrepancies
from app.db.models import Invoice, AuditLog
from app.schemas.invoice_schema import InvoiceExtractionResult
from app.config import settings

def _commit_with_retry(db_session, max_retries=3):
    """Retries db.commit() to handle SQLite lock errors gracefully."""
    for attempt in range(max_retries):
        try:
            db_session.commit()
            return
        except OperationalError as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                db_session.rollback()
                logger.warning(f"Database locked, retrying commit ({attempt+1}/{max_retries})...")
                time.sleep(0.5 * (attempt + 1))
            else:
                db_session.rollback()
                raise e

def process_invoice_email(email_payload, db_session) -> Invoice:
    """
    Orchestrates the entire end-to-end pipeline for a single email.
    """
    logger.info("Starting pipeline for email", extra={"pdf_path": email_payload.pdf_path})
    
    from datetime import datetime, timezone
    
    received_date = None
    if email_payload.received_at:
        try:
            received_str = email_payload.received_at.replace("Z", "+00:00")
            received_date = datetime.fromisoformat(received_str)
        except ValueError:
            logger.warning(f"Failed to parse received_at date: {email_payload.received_at}")
            
    if not received_date:
        received_date = datetime.now(timezone.utc)

    invoice_record = Invoice(
        sender_email=email_payload.sender_email,
        email_subject=email_payload.subject,
        invoice_attachment_path=email_payload.pdf_path,
        validation_status="Procurement Review", # default fallback
        extraction_warnings=[],
        received_at=received_date
    )
    
    try:
        # Step 1: Extract PDF text
        try:
            pdf_text = extract_text_from_pdf(email_payload.pdf_path)
        except PDFExtractionError as e:
            invoice_record.extraction_warnings = [str(e)]
            _save_and_log(db_session, invoice_record, "pipeline_failed")
            return invoice_record
            
        # Step 2: AI Extraction
        extraction_result = extract_invoice_data(pdf_text)
        
        # Populate DB record with extracted fields
        invoice_record.vendor_name = extraction_result.vendor_name
        invoice_record.vendor_id = extraction_result.vendor_id
        invoice_record.purchase_order_number = extraction_result.purchase_order_number
        invoice_record.invoice_number = extraction_result.invoice_number
        if extraction_result.invoice_date:
            try:
                from datetime import datetime
                invoice_record.invoice_date = datetime.strptime(extraction_result.invoice_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        invoice_record.currency = extraction_result.currency
        invoice_record.net_amount = extraction_result.net_amount
        invoice_record.tax_amount = extraction_result.tax_amount
        invoice_record.gross_amount = extraction_result.gross_amount
        invoice_record.line_items = [item.model_dump() for item in extraction_result.line_items]
        invoice_record.confidence_score = extraction_result.confidence_score
        invoice_record.extraction_warnings = extraction_result.extraction_warnings
        
        if extraction_result.extraction_failed:
            _save_and_log(db_session, invoice_record, "extraction_failed")
            return invoice_record
            
        # Step 2b: Duplicate Check (Bonus)
        if invoice_record.invoice_number and invoice_record.vendor_name:
            existing = db_session.query(Invoice).filter(
                Invoice.invoice_number == invoice_record.invoice_number,
                Invoice.vendor_name == invoice_record.vendor_name
            ).first()
            if existing:
                discrepancies = [Discrepancy(
                    type="duplicate_invoice",
                    severity="major",
                    field="invoice_number",
                    description=f"Duplicate invoice detected. Matches existing invoice ID {existing.id}."
                )]
                invoice_record.discrepancy_summary = summarize_discrepancies(discrepancies)
                invoice_record.validation_status = "Rejected"
                _save_and_log(db_session, invoice_record, "ingested_and_validated")
                return invoice_record
                
        # Step 3: PO Retrieval
        po = get_purchase_order(invoice_record.purchase_order_number, db_session)
        
        # Step 4-6: Matching & Discrepancies
        if not po:
            # Missing PO case
            discrepancies = detect_discrepancies(None, extraction_result, None)
            invoice_record.validation_status = "Rejected"
            invoice_record.discrepancy_summary = summarize_discrepancies(discrepancies)
        else:
            match_result = compare_invoice_to_po(extraction_result, po, settings.discrepancy_tolerance_percent)
            invoice_record.purchase_order_match = match_result.model_dump()
            
            discrepancies = detect_discrepancies(match_result, extraction_result, po)
            invoice_record.discrepancy_summary = summarize_discrepancies(discrepancies)
            invoice_record.validation_status = determine_validation_status(discrepancies)
            
        # Step 7: Persist Full Record
        _save_and_log(db_session, invoice_record, "ingested_and_validated")
        
        # Step 8: Push to Airtable (if configured)
        from app.integrations.airtable_client import push_invoice_to_airtable
        push_invoice_to_airtable(invoice_record)
        
        logger.info(f"Pipeline complete for invoice {invoice_record.invoice_number}. Status: {invoice_record.validation_status}")
        return invoice_record
        
    except Exception as e:
        logger.exception("Unhandled error in pipeline")
        invoice_record.extraction_warnings = invoice_record.extraction_warnings or []
        invoice_record.extraction_warnings.append(f"Internal Pipeline Error: {str(e)}")
        invoice_record.validation_status = "Procurement Review"
        _save_and_log(db_session, invoice_record, "pipeline_error")
        return invoice_record

def _save_and_log(db_session, invoice: Invoice, action: str):
    """Helper to save invoice and write audit log."""
    db_session.add(invoice)
    db_session.flush() # get invoice ID
    
    audit_log = AuditLog(
        invoice_id=invoice.id,
        action=action,
        new_value=invoice.validation_status,
        actor="system"
    )
    db_session.add(audit_log)
    _commit_with_retry(db_session)
    db_session.refresh(invoice)
