# pyrefly: ignore
# type: ignore
import os
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import Request, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.security import get_current_user, create_access_token, limiter
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Invoice, PurchaseOrder, AuditLog
from app.pipeline import process_invoice_email, _commit_with_retry
from app.ingestion.inbox_watcher import process_new_emails, mark_as_processed, EmailPayload
from app.ingestion.imap_fetcher import fetch_unread_emails
from app.config import settings

router = APIRouter()

class ReviewRequest(BaseModel):
    reviewer_comments: Optional[str] = None
    override_status: Optional[str] = None
    decision: Optional[str] = None # "approve" | "reject" | None
    actor: str = "reviewer"

class RejectRequest(BaseModel):
    reason: str
    actor: str = "reviewer"


@router.post("/token")
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != settings.admin_username or form_data.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/ingest")
@limiter.limit("5/minute")
def ingest_invoices(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Triggers the inbox watcher to scan for new emails and process them through the pipeline.
    """
    # Fetch from IMAP first (if enabled)
    fetch_unread_emails()
    
    new_emails = process_new_emails()
    processed_invoices = []
    
    for email in new_emails:
        invoice = process_invoice_email(email, db)
        processed_invoices.append(invoice)
        mark_as_processed(email)
        
    return {"processed": len(processed_invoices), "invoices": [{"id": inv.id, "status": inv.validation_status} for inv in processed_invoices]}

@router.post("/ingest/simulate-failure")
def simulate_failure(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    """
    Simulates a failure by passing a non-existent PDF, triggering graceful fallback.
    """
    fake_email = EmailPayload(
        folder_path="fake/path",
        sender_email="fake@example.com",
        subject="Simulated Failure",
        pdf_path="does_not_exist.pdf"
    )
    invoice = process_invoice_email(fake_email, db)
    return {"id": invoice.id, "status": invoice.validation_status, "warnings": invoice.extraction_warnings}

@router.get("/invoices")
def list_invoices(status: Optional[str] = None, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    query = db.query(Invoice)
    if status:
        query = query.filter(Invoice.validation_status == status)
    invoices = query.order_by(Invoice.received_at.desc()).all()
    return invoices

@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice or not invoice.invoice_attachment_path:
        raise HTTPException(status_code=404, detail="PDF not found")
    if not os.path.exists(invoice.invoice_attachment_path):
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
    return FileResponse(invoice.invoice_attachment_path, media_type="application/pdf")

@router.patch("/invoices/{invoice_id}/review")
def review_invoice(invoice_id: int, review: ReviewRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    old_status = invoice.validation_status
    
    if review.reviewer_comments:
        invoice.reviewer_comments = review.reviewer_comments
        
    if review.override_status:
        invoice.validation_status = review.override_status
    elif review.decision == "approve":
        invoice.validation_status = "Ready for Payment"
    elif review.decision == "reject":
        invoice.validation_status = "Rejected"
        
    invoice.last_updated = datetime.now(timezone.utc)
    
    # Audit log
    if old_status != invoice.validation_status or review.reviewer_comments:
        audit_log = AuditLog(
            invoice_id=invoice.id,
            action="manual_review",
            old_value=old_status,
            new_value=invoice.validation_status,
            actor=review.actor
        )
        db.add(audit_log)
        
    _commit_with_retry(db)
    db.refresh(invoice)
    return invoice

@router.post("/invoices/{invoice_id}/approve")
def approve_invoice(invoice_id: int, actor: str = Body(default="reviewer", embed=True), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    old_status = invoice.validation_status
    invoice.validation_status = "Ready for Payment"
    invoice.last_updated = datetime.now(timezone.utc)
    
    db.add(AuditLog(invoice_id=invoice.id, action="status_changed", old_value=old_status, new_value="Ready for Payment", actor=actor))
    _commit_with_retry(db)
    db.refresh(invoice)
    return invoice

@router.post("/invoices/{invoice_id}/pay")
def pay_invoice(invoice_id: int, actor: str = Body(default="system", embed=True), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    old_status = invoice.validation_status
    invoice.validation_status = "Paid"
    invoice.payment_done_at = datetime.now(timezone.utc)
    invoice.last_updated = datetime.now(timezone.utc)
    
    db.add(AuditLog(invoice_id=invoice.id, action="payment_processed", old_value=old_status, new_value="Paid", actor=actor))
    _commit_with_retry(db)
    db.refresh(invoice)
    return invoice

@router.post("/invoices/{invoice_id}/reject")
def reject_invoice(invoice_id: int, reject_req: RejectRequest, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    old_status = invoice.validation_status
    invoice.validation_status = "Rejected"
    
    # Append to existing comments
    existing_comments = invoice.reviewer_comments or ""
    invoice.reviewer_comments = f"{existing_comments}\nRejection Reason: {reject_req.reason}".strip()
    invoice.last_updated = datetime.now(timezone.utc)
    
    db.add(AuditLog(invoice_id=invoice.id, action="status_changed", old_value=old_status, new_value="Rejected", actor=reject_req.actor))
    _commit_with_retry(db)
    db.refresh(invoice)
    return invoice

@router.get("/purchase-orders")
def list_pos(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return db.query(PurchaseOrder).all()

@router.get("/audit-log/{invoice_id}")
def get_audit_log(invoice_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.invoice_id == invoice_id).order_by(AuditLog.timestamp.asc()).all()
    return logs

@router.get("/config")
def get_config(current_user: str = Depends(get_current_user)):
    return {
        "discrepancy_tolerance_percent": settings.discrepancy_tolerance_percent
    }

@router.get("/logs/recent")
def get_recent_logs(lines: int = 50, current_user: str = Depends(get_current_user)):
    """Tails the app.log file to return recent JSON log entries."""
    if not os.path.exists("app.log"):
        return []
        
    log_lines = []
    try:
        with open("app.log", "r") as f:
            all_lines = f.readlines()
            # Get last N lines
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
            for line in recent:
                try:
                    log_lines.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        return [{"error": str(e)}]
        
    return log_lines
