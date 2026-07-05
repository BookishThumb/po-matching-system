import pytest
from app.matching.po_matcher import compare_invoice_to_po
from app.schemas.invoice_schema import InvoiceExtractionResult, LineItem
from app.db.models import PurchaseOrder

def test_compare_invoice_to_po():
    po = PurchaseOrder(
        po_number="PO-1",
        vendor_name="Test Vendor",
        currency="USD",
        total_amount=100.0,
        line_items=[{"description": "Item A", "quantity": 10, "unit_price": 10.0, "total": 100.0}]
    )
    
    # Exact Match
    inv_exact = InvoiceExtractionResult(
        vendor_name="Test Vendor",
        purchase_order_number="PO-1",
        currency="USD",
        net_amount=100.0,
        line_items=[LineItem(description="Item A", quantity=10, unit_price=10.0, total=100.0)]
    )
    
    res_exact = compare_invoice_to_po(inv_exact, po, 2.0)
    assert next(f for f in res_exact.fields if f.field_name == "vendor_name").matched
    assert next(f for f in res_exact.fields if f.field_name == "total_amount").matched
    assert len(res_exact.line_items) == 1
    assert res_exact.line_items[0].status == "matched"
    assert res_exact.line_items[0].quantity_matched
    
    # Tolerance Match (1% diff)
    inv_tol = InvoiceExtractionResult(
        vendor_name="Test Vendor",
        purchase_order_number="PO-1",
        currency="USD",
        net_amount=101.0,
        line_items=[LineItem(description="Item A", quantity=10, unit_price=10.1, total=101.0)]
    )
    res_tol = compare_invoice_to_po(inv_tol, po, 2.0)
    assert next(f for f in res_tol.fields if f.field_name == "total_amount").matched # 1% < 2%
    assert res_tol.line_items[0].unit_price_matched # 1% < 2%
    
    # Mismatch (>2% diff)
    inv_mis = InvoiceExtractionResult(
        vendor_name="Different Vendor",
        purchase_order_number="PO-1",
        currency="USD",
        net_amount=110.0,
        line_items=[LineItem(description="Item A", quantity=10, unit_price=11.0, total=110.0)]
    )
    res_mis = compare_invoice_to_po(inv_mis, po, 2.0)
    assert not next(f for f in res_mis.fields if f.field_name == "vendor_name").matched
    assert not next(f for f in res_mis.fields if f.field_name == "total_amount").matched
    assert not res_mis.line_items[0].unit_price_matched

