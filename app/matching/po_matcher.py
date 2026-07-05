import difflib
from typing import Optional
from app.db.models import PurchaseOrder
from app.schemas.invoice_schema import InvoiceExtractionResult, MatchResult, FieldMatch, LineItemMatch
from app.utils.logger import logger

def get_purchase_order(po_number: str, db_session) -> Optional[PurchaseOrder]:
    """Retrieves a PurchaseOrder from the database by po_number."""
    if not po_number:
        return None
    return db_session.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first()

def _calculate_diff_percent(invoice_val: float, po_val: float) -> float:
    """Calculates percentage difference relative to PO value."""
    if not po_val:
        return 100.0 if invoice_val else 0.0
    return abs(invoice_val - po_val) / po_val * 100

def compare_invoice_to_po(invoice: InvoiceExtractionResult, po: PurchaseOrder, tolerance_percent: float) -> MatchResult:
    """
    Compares extracted invoice fields against the PO.
    Returns a MatchResult populated with field-by-field matches.
    """
    logger.info(f"Comparing invoice against PO {po.po_number} with {tolerance_percent}% tolerance")
    result = MatchResult()

    # Vendor Match (fuzzy string)
    vendor_matched = False
    if invoice.vendor_name and po.vendor_name:
        # Lowercase, remove common punctuation and spaces for robust comparison
        inv_v = "".join(e for e in invoice.vendor_name.lower() if e.isalnum())
        po_v = "".join(e for e in po.vendor_name.lower() if e.isalnum())
        ratio = difflib.SequenceMatcher(None, inv_v, po_v).ratio()
        vendor_matched = ratio > 0.85 # Allow minor typos
        
    result.fields.append(FieldMatch(
        field_name="vendor_name",
        invoice_value=invoice.vendor_name,
        po_value=po.vendor_name,
        matched=vendor_matched
    ))
    
    # PO Number
    po_num_matched = invoice.purchase_order_number == po.po_number
    result.fields.append(FieldMatch(
        field_name="purchase_order_number",
        invoice_value=invoice.purchase_order_number,
        po_value=po.po_number,
        matched=po_num_matched
    ))

    # Currency
    curr_matched = invoice.currency == po.currency
    result.fields.append(FieldMatch(
        field_name="currency",
        invoice_value=invoice.currency,
        po_value=po.currency,
        matched=curr_matched
    ))

    # Total Amount
    inv_total = invoice.gross_amount or invoice.net_amount or 0.0
    diff_pct = _calculate_diff_percent(inv_total, po.total_amount)
    total_matched = diff_pct <= tolerance_percent
    
    result.fields.append(FieldMatch(
        field_name="total_amount",
        invoice_value=inv_total,
        po_value=po.total_amount,
        matched=total_matched,
        difference_percent=diff_pct
    ))

    # Line Items Match
    po_items_matched_indices = set()
    
    for i, inv_item in enumerate(invoice.line_items):
        best_po_idx = None
        best_ratio = 0
        
        # Find best matching PO line by description
        if inv_item.description:
            inv_desc = str(inv_item.description).lower()
            for j, po_item in enumerate(po.line_items):
                if j in po_items_matched_indices:
                    continue
                ratio = difflib.SequenceMatcher(None, inv_desc, str(po_item.get("description", "")).lower()).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_po_idx = j

        if best_po_idx is not None and best_ratio > 0.6: # Found a likely match
            po_items_matched_indices.add(best_po_idx)
            po_item = po.line_items[best_po_idx]
            
            qty_diff = _calculate_diff_percent(inv_item.quantity or 0, po_item.get("quantity", 0))
            price_diff = _calculate_diff_percent(inv_item.unit_price or 0, po_item.get("unit_price", 0))
            
            result.line_items.append(LineItemMatch(
                invoice_index=i,
                po_index=best_po_idx,
                invoice_description=inv_item.description,
                po_description=po_item.get("description"),
                quantity_matched=qty_diff <= tolerance_percent,
                quantity_diff_percent=qty_diff,
                unit_price_matched=price_diff <= tolerance_percent,
                unit_price_diff_percent=price_diff,
                status="matched"
            ))
        else:
            # Extra on invoice
            result.line_items.append(LineItemMatch(
                invoice_index=i,
                invoice_description=inv_item.description,
                status="extra_on_invoice"
            ))

    # Missing on invoice
    for j, po_item in enumerate(po.line_items):
        if j not in po_items_matched_indices:
            result.line_items.append(LineItemMatch(
                po_index=j,
                po_description=po_item.get("description"),
                status="missing_on_invoice"
            ))

    return result
