import argparse
from app.db.database import engine, Base, SessionLocal
from app.db.models import PurchaseOrder

# Sample PO data exactly as requested for varied test cases
SAMPLE_POS = [
    {
        "po_number": "PO-1001",
        "vendor_name": "Bright Steel Supplies",
        "vendor_id": "V-001",
        "currency": "USD",
        "line_items": [
            {"description": "Steel rods", "quantity": 100, "unit_price": 5.0, "total": 500.0},
            {"description": "Bolts", "quantity": 500, "unit_price": 0.5, "total": 250.0},
            {"description": "Washers", "quantity": 1000, "unit_price": 0.1, "total": 100.0},
        ],
        "total_amount": 850.0,
    },
    {
        "po_number": "PO-1002",
        "vendor_name": "Nordic Paper Co.",
        "vendor_id": "V-002",
        "currency": "EUR",
        "line_items": [
            {"description": "A4 Paper Reams", "quantity": 20, "unit_price": 4.5, "total": 90.0},
            {"description": "Cardstock", "quantity": 10, "unit_price": 12.0, "total": 120.0},
        ],
        "total_amount": 210.0,
    },
    {
        "po_number": "PO-1003",
        "vendor_name": "Apex Logistics Ltd",
        "vendor_id": "V-003",
        "currency": "USD",
        "line_items": [
            {"description": "Pallet delivery", "quantity": 5, "unit_price": 150.0, "total": 750.0},
            {"description": "Express fee", "quantity": 1, "unit_price": 50.0, "total": 50.0},
            {"description": "Insurance", "quantity": 1, "unit_price": 25.0, "total": 25.0},
            {"description": "Packaging", "quantity": 10, "unit_price": 5.0, "total": 50.0},
        ],
        "total_amount": 875.0,
    },
    {
        "po_number": "PO-1004",
        "vendor_name": "Quantum Circuits Inc",
        "vendor_id": "V-004",
        "currency": "USD",
        "line_items": [
            {"description": "Microcontroller", "quantity": 200, "unit_price": 15.0, "total": 3000.0},
            {"description": "Sensor Module", "quantity": 150, "unit_price": 25.0, "total": 3750.0},
        ],
        "total_amount": 6750.0,
    },
    {
        "po_number": "PO-1005",
        "vendor_name": "GreenLeaf Packaging",
        "vendor_id": "V-005",
        "currency": "GBP",
        "line_items": [
            {"description": "Cardboard Boxes (Large)", "quantity": 300, "unit_price": 1.5, "total": 450.0},
            {"description": "Bubble Wrap", "quantity": 50, "unit_price": 10.0, "total": 500.0},
            {"description": "Packing Tape", "quantity": 100, "unit_price": 2.0, "total": 200.0},
        ],
        "total_amount": 1150.0,
    },
    {
        "po_number": "PO-1006",
        "vendor_name": "Titan Industrial Parts",
        "vendor_id": "V-006",
        "currency": "USD",
        "line_items": [
            {"description": "Hydraulic Pump", "quantity": 2, "unit_price": 450.0, "total": 900.0},
            {"description": "Filter Elements", "quantity": 10, "unit_price": 35.0, "total": 350.0},
            {"description": "O-Ring Kit", "quantity": 5, "unit_price": 15.0, "total": 75.0},
        ],
        "total_amount": 1325.0,
    },
    {
        "po_number": "PO-1007",
        "vendor_name": "Meridian Office Supplies",
        "vendor_id": "V-007",
        "currency": "USD",
        "line_items": [
            {"description": "Whiteboard Markers", "quantity": 50, "unit_price": 1.2, "total": 60.0},
            {"description": "Erasers", "quantity": 20, "unit_price": 2.0, "total": 40.0},
        ],
        "total_amount": 100.0,
    },
    {
        "po_number": "PO-1008",
        "vendor_name": "Missing Reference PO",
        "vendor_id": "V-008",
        "currency": "USD",
        "line_items": [
            {"description": "Item", "quantity": 1, "unit_price": 100.0, "total": 100.0},
        ],
        "total_amount": 100.0,
    }
]


def seed_db(reset=False):
    if reset:
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Seeding database with Purchase Orders...")
    inserted = 0
    skipped = 0
    for po_data in SAMPLE_POS:
        existing = db.query(PurchaseOrder).filter_by(po_number=po_data["po_number"]).first()
        if not existing:
            po = PurchaseOrder(**po_data)
            db.add(po)
            inserted += 1
        else:
            skipped += 1
            
    db.commit()
    
    print("\n--- Seed Summary ---")
    print(f"Inserted: {inserted}")
    print(f"Skipped (already exists): {skipped}")
    print("\n--- Current Purchase Orders in Database ---")
    
    # Print summary table
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.po_number).all()
    print(f"{'PO Number':<10} | {'Vendor Name':<30} | {'Total':<10} | {'Currency'}")
    print("-" * 65)
    for po in pos:
        print(f"{po.po_number:<10} | {po.vendor_name:<30} | {po.total_amount:<10} | {po.currency}")
        
    db.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed PO database")
    parser.add_argument("--reset", action="store_true", help="Drop tables before seeding")
    args = parser.parse_args()
    
    seed_db(reset=args.reset)
