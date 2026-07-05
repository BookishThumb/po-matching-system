import os
import time
import json
from pathlib import Path

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.seed import seed_db
from app.db.models import PurchaseOrder
from app.pipeline import process_invoice_email
from app.ingestion.inbox_watcher import EmailPayload

EXPECTED = {
    "01_clean_match": "Ready for Payment",
    "02_vendor_mismatch": "Rejected",
    "03_quantity_mismatch_major": "Rejected",
    "04_price_mismatch_minor": "Procurement Review",
    "05_extra_line_item": "Procurement Review",
    "06_missing_line_item": "Rejected", # Assuming major
    "07_within_tolerance": "Ready for Payment",
    "08_missing_po": "Rejected",
    "09_incorrect_tax": "Rejected", # Or Procurement Review
    "10_total_exceeds_po": "Rejected",
    "11_malformed_scenario": "Procurement Review",
    "12_duplicate_test": "Rejected"
}

def main():
    # 1. Ensure DB is seeded
    db = SessionLocal()
    pos = db.query(PurchaseOrder).count()
    if pos == 0:
        print("Database not seeded. Seeding now...")
        seed_db(reset=True)
    db.close()

    emails_dir = Path("sample_data/emails")
    if not emails_dir.exists():
        print("Error: sample_data/emails not found. Run generate script first.")
        return

    folders = sorted([d for d in emails_dir.iterdir() if d.is_dir()])
    
    passed = 0
    failed = 0
    failures = []
    
    print("\n--- Running Full Test Suite ---\n")

    for folder in folders:
        folder_name = folder.name
        pdf_path = folder / "invoice.pdf"
        meta_path = folder / "metadata.json"
        
        if not pdf_path.exists() or not meta_path.exists():
            continue
            
        with open(meta_path, "r") as f:
            meta = json.load(f)
            
        payload = EmailPayload(
            folder_path=str(folder),
            sender_email=meta["sender_email"],
            subject=meta["subject"],
            pdf_path=str(pdf_path)
        )
        
        db = SessionLocal()
        invoice_record = process_invoice_email(payload, db)
        db.close()
        
        actual = invoice_record.validation_status
        # Handle flexible expectations
        expected = EXPECTED.get(folder_name, "Unknown")
        
        is_pass = False
        if actual == expected:
            is_pass = True
        elif expected == "Procurement Review / Rejected" and actual in ["Procurement Review", "Rejected"]:
            is_pass = True
        elif folder_name == "06_missing_line_item" and actual in ["Procurement Review", "Rejected"]:
            is_pass = True
        elif folder_name == "09_incorrect_tax" and actual in ["Procurement Review", "Rejected"]:
            is_pass = True
            
        if is_pass:
            print(f"[PASS] {folder_name}.pdf -> {actual}")
            passed += 1
        else:
            print(f"[FAIL] {folder_name}.pdf -> {actual} (expected: {expected})")
            failed += 1
            failures.append((folder_name, actual, expected, invoice_record.discrepancy_summary))
            
        time.sleep(1) # Delay to respect rate limits

    print("\n--- Summary ---")
    print(f"Total Run: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failures:
        print("\n--- Failure Details ---")
        for fail in failures:
            print(f"\nTest: {fail[0]}")
            print(f"Expected: {fail[2]}, Actual: {fail[1]}")
            print(f"Discrepancies: {fail[3]}")

if __name__ == "__main__":
    main()
