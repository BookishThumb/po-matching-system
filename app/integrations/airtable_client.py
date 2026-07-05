import json
from pyairtable import Api
from app.config import settings
from app.utils.logger import logger
from app.db.models import Invoice

def push_invoice_to_airtable(invoice: Invoice):
    """
    Pushes an Invoice record to Airtable if configured.
    """
    if not settings.airtable_api_key or not settings.airtable_base_id:
        logger.debug("Airtable not configured, skipping export.")
        return

    try:
        api = Api(settings.airtable_api_key)
        table = api.table(settings.airtable_base_id, settings.airtable_table_name)
        
        # Prepare the record dictionary
        record_fields = {
            "Vendor Name": invoice.vendor_name or "Unknown",
            "Invoice Number": invoice.invoice_number or "",
            "PO Number": invoice.purchase_order_number or "",
            "Status": invoice.validation_status or "",
            "Gross Amount": float(invoice.gross_amount) if invoice.gross_amount is not None else 0.0,
            "Currency": invoice.currency or "",
            "PDF Local Path": invoice.invoice_attachment_path or ""
        }
        
        if invoice.invoice_date:
            record_fields["Invoice Date"] = str(invoice.invoice_date)
            
        if invoice.discrepancy_summary:
            try:
                if isinstance(invoice.discrepancy_summary, list):
                    # convert array to nicely formatted string
                    summaries = [f"[{d.get('severity', 'minor').upper()}] {d.get('description', '')}" for d in invoice.discrepancy_summary]
                    record_fields["Discrepancies"] = "\n".join(summaries)
                else:
                    record_fields["Discrepancies"] = json.dumps(invoice.discrepancy_summary, indent=2)
            except Exception:
                pass
                
        # Push to Airtable
        created = table.create(record_fields)
        logger.info(f"Successfully exported invoice {invoice.id} to Airtable (Record ID: {created['id']})")
        
    except Exception as e:
        logger.error(f"Failed to push to Airtable: {e}")
