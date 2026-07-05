import os
import time
import json
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.pipeline import process_invoice_email
from app.ingestion.inbox_watcher import EmailPayload

DEMO_SEQUENCE = [
    ("01_clean_match", "Here's a clean invoice that matches its PO exactly."),
    ("02_vendor_mismatch", "Now a vendor mismatch — the AI should catch this as a major discrepancy."),
    ("07_within_tolerance", "This one's slightly off, but within our 2% tolerance — should still pass."),
    ("08_missing_po", "This invoice references a PO number that doesn't exist in our system."),
    ("11_malformed_scenario", "And finally, a messy invoice — watch how the AI flags low confidence instead of guessing.")
]

def main():
    emails_dir = Path("sample_data/emails")
    
    print("\n--- Starting Quick Demo Subset ---\n")

    for folder_name, narration in DEMO_SEQUENCE:
        folder = emails_dir / folder_name
        pdf_path = folder / "invoice.pdf"
        meta_path = folder / "metadata.json"
        
        if not pdf_path.exists() or not meta_path.exists():
            print(f"Skipping {folder_name} - files not found.")
            continue
            
        print(f"\n🗣 NARRATION HINT: \"{narration}\"")
        time.sleep(2) # Give speaker time to read
        print(f"Processing {folder_name}.pdf...")
        
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
        
        print(f"Result: {invoice_record.validation_status}")
        time.sleep(1)

    print("\n--- Demo Complete ---")

if __name__ == "__main__":
    main()
