import pytest
from app.matching.validation_rules import determine_validation_status
from app.matching.discrepancy import Discrepancy

def test_determine_validation_status():
    # No discrepancies
    assert determine_validation_status([]) == "Ready for Payment"
    
    # Only minor
    minors = [
        Discrepancy(type="unit_price_mismatch", severity="minor", field="line_items", description="small diff"),
        Discrepancy(type="additional_line_items", severity="minor", field="line_items", description="shipping")
    ]
    assert determine_validation_status(minors) == "Procurement Review"
    
    # Any major
    majors = [
        Discrepancy(type="unit_price_mismatch", severity="minor", field="line_items", description="small diff"),
        Discrepancy(type="vendor_mismatch", severity="major", field="vendor_name", description="Wrong vendor")
    ]
    assert determine_validation_status(majors) == "Rejected"

