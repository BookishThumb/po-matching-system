from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Date, ForeignKey, Text
from datetime import datetime, timezone
from app.db.database import Base

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    po_number = Column(String, unique=True, index=True, nullable=False)
    vendor_name = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    line_items = Column(JSON, nullable=False) # list of {description, quantity, unit_price, total}
    total_amount = Column(Float, nullable=False)
    approval_status = Column(String, default="Approved")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PurchaseOrder(po_number={self.po_number}, vendor={self.vendor_name}, total={self.total_amount})>"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_name = Column(String, nullable=True)
    vendor_id = Column(String, nullable=True)
    purchase_order_number = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    currency = Column(String, nullable=True)
    net_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    gross_amount = Column(Float, nullable=True)
    line_items = Column(JSON, nullable=True)
    
    # Matching fields
    purchase_order_match = Column(JSON, nullable=True)
    discrepancy_summary = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    extraction_warnings = Column(JSON, nullable=True)
    validation_status = Column(String, nullable=True) # "Ready for Payment" | "Procurement Review" | "Rejected"
    reviewer_comments = Column(Text, nullable=True)
    invoice_attachment_path = Column(String, nullable=True)
    sender_email = Column(String, nullable=True)
    email_subject = Column(String, nullable=True)
    
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    payment_done_at = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Invoice(invoice_number={self.invoice_number}, po_number={self.purchase_order_number}, status={self.validation_status})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    action = Column(String, nullable=False) # e.g. "status_changed", "extracted", "reviewed"
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    actor = Column(String, default="system")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<AuditLog(invoice_id={self.invoice_id}, action={self.action}, timestamp={self.timestamp})>"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="reviewer")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
