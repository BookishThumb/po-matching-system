from pydantic import BaseModel, Field
from typing import List

class POLineItemSchema(BaseModel):
    description: str
    quantity: float
    unit_price: float
    total: float

class PurchaseOrderSchema(BaseModel):
    id: int
    po_number: str
    vendor_name: str
    vendor_id: str
    currency: str
    line_items: List[POLineItemSchema]
    total_amount: float
    approval_status: str

    model_config = {"from_attributes": True}
