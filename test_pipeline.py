from app.db.database import SessionLocal
from app.ingestion.inbox_watcher import process_new_emails
from app.pipeline import process_invoice_email

db = SessionLocal()
emails = process_new_emails()
print(f"Found {len(emails)} emails")
for email in emails:
    invoice = process_invoice_email(email, db)
    print(f"Invoice {invoice.id}: received_at={invoice.received_at}, status={invoice.validation_status}")
