from typing import List
from app.matching.discrepancy import Discrepancy

def determine_validation_status(discrepancies: List[Discrepancy]) -> str:
    """
    Business Rules for Invoice Status:
    - No discrepancies at all -> "Ready for Payment"
    - Only minor discrepancies -> "Procurement Review"
    - Any major discrepancy -> "Rejected"
    - Missing PO (always major) -> "Rejected"
    """
    if not discrepancies:
        return "Ready for Payment"
        
    has_major = any(d.severity == "major" for d in discrepancies)
    
    if has_major:
        return "Rejected"
        
    # If there are discrepancies, but none are major
    return "Procurement Review"

def summarize_discrepancies(discrepancies: List[Discrepancy]) -> List[dict]:
    """
    Produces a list of dictionaries suitable for JSON storage in the database.
    """
    return [d.model_dump() for d in discrepancies]
