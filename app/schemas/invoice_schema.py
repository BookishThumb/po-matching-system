from pydantic import BaseModel, Field, validator
from typing import List, Optional

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None

class InvoiceExtractionResult(BaseModel):
    vendor_name: Optional[str] = None
    vendor_id: Optional[str] = None
    purchase_order_number: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    net_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_amount: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    extraction_warnings: List[str] = Field(default_factory=list)
    extraction_failed: bool = Field(default=False, exclude=True) # Used internally to flag total parse failure

# Schemas for matching results
class FieldMatch(BaseModel):
    field_name: str
    invoice_value: Optional[str | float] = None
    po_value: Optional[str | float] = None
    matched: bool
    difference_percent: Optional[float] = None

class LineItemMatch(BaseModel):
    invoice_index: Optional[int] = None
    po_index: Optional[int] = None
    invoice_description: Optional[str] = None
    po_description: Optional[str] = None
    quantity_matched: bool = False
    quantity_diff_percent: Optional[float] = None
    unit_price_matched: bool = False
    unit_price_diff_percent: Optional[float] = None
    status: str # "matched", "missing_on_invoice", "extra_on_invoice"

class MatchResult(BaseModel):
    fields: List[FieldMatch] = Field(default_factory=list)
    line_items: List[LineItemMatch] = Field(default_factory=list)
