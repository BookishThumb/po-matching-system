from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas.invoice_schema import MatchResult, InvoiceExtractionResult
from app.db.models import PurchaseOrder

class Discrepancy(BaseModel):
    type: str
    severity: str # "minor" | "major"
    field: str
    description: str

def detect_discrepancies(match_result: MatchResult, invoice: InvoiceExtractionResult, po: PurchaseOrder) -> List[Discrepancy]:
    """
    Analyzes a MatchResult and identifies business rule discrepancies.
    Threshold for numeric differences: <10% is minor, >=10% is major.
    """
    discrepancies = []
    
    if not po:
        discrepancies.append(Discrepancy(
            type="missing_purchase_order",
            severity="major",
            field="purchase_order_number",
            description=f"Purchase order '{invoice.purchase_order_number}' could not be found."
        ))
        return discrepancies # Can't detect anything else without a PO

    # Vendor Mismatch
    vendor_match = next((f for f in match_result.fields if f.field_name == "vendor_name"), None)
    if vendor_match and not vendor_match.matched:
        discrepancies.append(Discrepancy(
            type="vendor_mismatch",
            severity="major",
            field="vendor_name",
            description=f"Invoice vendor '{vendor_match.invoice_value}' does not match PO vendor '{vendor_match.po_value}'."
        ))

    # Total Amount
    total_match = next((f for f in match_result.fields if f.field_name == "total_amount"), None)
    if total_match and not total_match.matched:
        diff_pct = total_match.difference_percent or 0.0
        # If invoice exceeds PO value significantly, flag as major
        if (total_match.invoice_value or 0) > (total_match.po_value or 0) and diff_pct >= 10.0:
            sev = "major"
        else:
            sev = "minor" if diff_pct < 10.0 else "major"
            
        discrepancies.append(Discrepancy(
            type="invoice_total_exceeds_po_value",
            severity=sev,
            field="total_amount",
            description=f"Invoice total ({total_match.invoice_value}) differs from PO total ({total_match.po_value}) by {diff_pct:.1f}%."
        ))

    # Line Items
    for item in match_result.line_items:
        if item.status == "missing_on_invoice":
            discrepancies.append(Discrepancy(
                type="missing_line_items",
                severity="major",
                field="line_items",
                description=f"PO item '{item.po_description}' is missing from the invoice."
            ))
        elif item.status == "extra_on_invoice":
            # Just mark all extras as minor for now, could be shipping/handling
            discrepancies.append(Discrepancy(
                type="additional_line_items",
                severity="minor",
                field="line_items",
                description=f"Invoice contains extra item '{item.invoice_description}' not on PO."
            ))
        elif item.status == "matched":
            if not item.quantity_matched:
                diff_pct = item.quantity_diff_percent or 0.0
                sev = "minor" if diff_pct < 10.0 else "major"
                discrepancies.append(Discrepancy(
                    type="quantity_mismatch",
                    severity=sev,
                    field=f"line_items[{item.invoice_index}].quantity",
                    description=f"Quantity mismatch for '{item.invoice_description}' (Diff: {diff_pct:.1f}%)."
                ))
            if not item.unit_price_matched:
                diff_pct = item.unit_price_diff_percent or 0.0
                sev = "minor" if diff_pct < 10.0 else "major"
                discrepancies.append(Discrepancy(
                    type="unit_price_mismatch",
                    severity=sev,
                    field=f"line_items[{item.invoice_index}].unit_price",
                    description=f"Unit price mismatch for '{item.invoice_description}' (Diff: {diff_pct:.1f}%)."
                ))

    # Tax Calculation
    if invoice.tax_amount is not None and invoice.net_amount is not None:
        expected_gross = invoice.net_amount + invoice.tax_amount
        actual_gross = invoice.gross_amount or 0.0
        # If gross != net + tax (allowing tiny float error)
        if abs(expected_gross - actual_gross) > 0.05:
            discrepancies.append(Discrepancy(
                type="incorrect_tax_calculation",
                severity="minor",
                field="tax_amount",
                description="Invoice gross amount does not equal net amount plus tax amount."
            ))

    return discrepancies
