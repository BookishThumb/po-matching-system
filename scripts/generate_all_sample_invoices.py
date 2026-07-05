import os
import json
from pathlib import Path
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from app.db.seed import SAMPLE_POS

def get_po(po_num):
    for p in SAMPLE_POS:
        if p["po_number"] == po_num:
            return p
    return None

def draw_invoice(c, data):
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 750, data.get("vendor_name", "Unknown Vendor"))
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Vendor ID: {data.get('vendor_id', '')}")
    c.drawString(50, 710, f"Date: {data.get('invoice_date', '2026-07-03')}")
    c.drawString(50, 690, f"Due Date: {data.get('due_date', '2026-08-03')}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(400, 750, "INVOICE")
    c.setFont("Helvetica", 12)
    c.drawString(400, 730, f"Invoice #: {data.get('invoice_number', '')}")
    c.drawString(400, 710, f"PO #: {data.get('po_number', '')}")
    
    y = 630
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Description")
    c.drawString(300, y, "Quantity")
    c.drawString(400, y, "Unit Price")
    c.drawString(500, y, "Total")
    c.line(50, y-5, 550, y-5)
    
    y -= 25
    c.setFont("Helvetica", 12)
    for item in data.get("line_items", []):
        c.drawString(50, y, item.get("description", ""))
        c.drawString(300, y, str(item.get("quantity", "")))
        c.drawString(400, y, f"{item.get('unit_price', ''):.2f}")
        c.drawString(500, y, f"{item.get('total', ''):.2f}")
        y -= 20
        
    y -= 20
    c.line(50, y, 550, y)
    y -= 25
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y, "Net Amount:")
    c.drawString(500, y, f"{data.get('net_amount', 0):.2f}")
    y -= 20
    c.drawString(400, y, "Tax Amount:")
    c.drawString(500, y, f"{data.get('tax_amount', 0):.2f}")
    y -= 20
    c.drawString(400, y, "Gross Amount:")
    c.drawString(500, y, f"{data.get('gross_amount', 0):.2f} {data.get('currency', '')}")

def generate_pdf(filename, folder_name, data):
    emails_dir = Path("sample_data/emails")
    folder_path = emails_dir / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    
    pdf_path = folder_path / "invoice.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    if data.get("malformed"):
        c.setFont("Helvetica", 16)
        c.drawString(50, 700, "INVOICE DOC")
        c.drawString(50, 650, "Please pay us 500 dollars.")
        c.drawString(50, 600, "For goods.")
    else:
        draw_invoice(c, data)
    c.save()
    
    metadata = {
        "sender_name": f"{data.get('vendor_name', 'Unknown')} Billing",
        "sender_email": f"billing@{data.get('vendor_name', 'unknown').replace(' ', '').lower()}.com",
        "subject": f"Invoice {data.get('invoice_number', '')} for PO {data.get('po_number', '')}",
        "received_at": datetime.now(timezone.utc).isoformat()
    }
    with open(folder_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

def main():
    cases = []
    
    # 1. Clean Match
    po = get_po("PO-1001")
    data = po.copy()
    data["invoice_number"] = "INV-1001-01"
    data["net_amount"] = po["total_amount"]
    data["tax_amount"] = 0
    data["gross_amount"] = po["total_amount"]
    cases.append(("01_clean_match", data))
    
    # 2. Vendor Mismatch
    po = get_po("PO-1002")
    data = po.copy()
    data["invoice_number"] = "INV-1002-02"
    data["vendor_name"] = "Random Company Ltd"
    data["net_amount"] = po["total_amount"]
    data["tax_amount"] = 0
    data["gross_amount"] = po["total_amount"]
    cases.append(("02_vendor_mismatch", data))
    
    # 3. Quantity Mismatch Major
    po = get_po("PO-1003")
    data = po.copy()
    data["line_items"] = [item.copy() for item in po["line_items"]]
    data["line_items"][0]["quantity"] = 15  # Was 5
    data["line_items"][0]["total"] = 2250.0
    data["invoice_number"] = "INV-1003-03"
    data["net_amount"] = 2375.0
    data["tax_amount"] = 0
    data["gross_amount"] = 2375.0
    cases.append(("03_quantity_mismatch_major", data))
    
    # 4. Price Mismatch Minor
    po = get_po("PO-1004")
    data = po.copy()
    data["line_items"] = [item.copy() for item in po["line_items"]]
    data["line_items"][0]["unit_price"] = 16.0  # Was 15.0
    data["line_items"][0]["total"] = 3200.0
    data["invoice_number"] = "INV-1004-04"
    data["net_amount"] = 6950.0
    data["tax_amount"] = 0
    data["gross_amount"] = 6950.0
    cases.append(("04_price_mismatch_minor", data))
    
    # 5. Extra Line Item
    po = get_po("PO-1005")
    data = po.copy()
    data["line_items"] = [item.copy() for item in po["line_items"]]
    data["line_items"].append({"description": "Fragile Stickers", "quantity": 10, "unit_price": 5.0, "total": 50.0})
    data["invoice_number"] = "INV-1005-05"
    data["net_amount"] = 1200.0
    data["tax_amount"] = 0
    data["gross_amount"] = 1200.0
    cases.append(("05_extra_line_item", data))
    
    # 6. Missing Line Item
    po = get_po("PO-1006")
    data = po.copy()
    data["line_items"] = [item.copy() for item in po["line_items"] if item["description"] != "Filter Elements"]
    data["invoice_number"] = "INV-1006-06"
    data["net_amount"] = 975.0
    data["tax_amount"] = 0
    data["gross_amount"] = 975.0
    cases.append(("06_missing_line_item", data))
    
    # 7. Within Tolerance
    po = get_po("PO-1007")
    data = po.copy()
    data["line_items"] = [item.copy() for item in po["line_items"]]
    data["line_items"][0]["unit_price"] = 1.21  # Was 1.20
    data["line_items"][0]["total"] = 60.5
    data["invoice_number"] = "INV-1007-07"
    data["net_amount"] = 100.5
    data["tax_amount"] = 0
    data["gross_amount"] = 100.5
    cases.append(("07_within_tolerance", data))
    
    # 8. Missing PO
    data = {
        "vendor_name": "Ghost Corp",
        "po_number": "PO-9999",
        "invoice_number": "INV-9999-08",
        "currency": "USD",
        "line_items": [{"description": "Stuff", "quantity": 1, "unit_price": 100.0, "total": 100.0}],
        "net_amount": 100.0,
        "tax_amount": 0.0,
        "gross_amount": 100.0
    }
    cases.append(("08_missing_po", data))
    
    # 9. Incorrect Tax
    po = get_po("PO-1001")
    data = po.copy()
    data["invoice_number"] = "INV-1001-TAX"
    data["net_amount"] = po["total_amount"]
    data["tax_amount"] = 212.5  # 25% tax!
    data["gross_amount"] = po["total_amount"] + 212.5
    cases.append(("09_incorrect_tax", data))
    
    # 10. Total Exceeds PO
    po = get_po("PO-1003")
    data = po.copy()
    data["invoice_number"] = "INV-1003-EXCEED"
    data["net_amount"] = 2000.0
    data["tax_amount"] = 0.0
    data["gross_amount"] = 2000.0
    cases.append(("10_total_exceeds_po", data))
    
    # 11. Malformed Scenario
    data = {"malformed": True, "invoice_number": "???", "po_number": "???"}
    cases.append(("11_malformed_scenario", data))
    
    # 12. Duplicate Test
    po = get_po("PO-1001")
    data = po.copy()
    data["invoice_number"] = "INV-1001-01" # Matches case 1
    data["net_amount"] = po["total_amount"]
    data["tax_amount"] = 0
    data["gross_amount"] = po["total_amount"]
    cases.append(("12_duplicate_test", data))

    print(f"{'Filename':<30} | {'Targets PO':<15} | {'Expected Result'}")
    print("-" * 70)
    expected_results = {
        "01_clean_match": "Ready for Payment",
        "02_vendor_mismatch": "Rejected",
        "03_quantity_mismatch_major": "Rejected",
        "04_price_mismatch_minor": "Procurement Review",
        "05_extra_line_item": "Procurement Review",
        "06_missing_line_item": "Procurement Review / Rejected",
        "07_within_tolerance": "Ready for Payment",
        "08_missing_po": "Rejected",
        "09_incorrect_tax": "Procurement Review / Rejected",
        "10_total_exceeds_po": "Rejected",
        "11_malformed_scenario": "Procurement Review",
        "12_duplicate_test": "Rejected"
    }

    # Clear existing sample_data/emails folder first to avoid conflicts? 
    # Actually just create them in a new structure or overwrite
    import shutil
    if Path("sample_data/emails").exists():
        shutil.rmtree("sample_data/emails")
    
    for filename, data in cases:
        generate_pdf(f"{filename}.pdf", filename, data)
        print(f"{filename + '.pdf':<30} | {data.get('po_number', 'N/A'):<15} | {expected_results[filename]}")

if __name__ == "__main__":
    main()
