import pytest
from app.ai.extractor import extract_invoice_data
from app.schemas.invoice_schema import InvoiceExtractionResult
from app.ai.groq_client import GroqAPIError

def test_extraction_stub(monkeypatch):
    # Mock groq response
    def mock_call_groq(prompt, user_prompt):
        if "malformed" in user_prompt:
            return '{"vendor_name": "Test", "net_amount": "invalid_float"}'
        elif "fatal" in user_prompt:
            raise GroqAPIError("API down")
        return '{"vendor_name": "Acme Corp", "invoice_number": "123", "net_amount": 100.0, "confidence_score": 0.9, "line_items": []}'
        
    monkeypatch.setattr("app.ai.extractor.call_groq", mock_call_groq)
    
    # Valid extraction
    res = extract_invoice_data("good pdf text")
    assert res.vendor_name == "Acme Corp"
    assert res.net_amount == 100.0
    assert not res.extraction_failed
    
    # Malformed JSON triggers fallback and fail
    res_fail = extract_invoice_data("malformed pdf text")
    assert res_fail.extraction_failed
    assert len(res_fail.extraction_warnings) > 0
    
    # API Exception
    res_exc = extract_invoice_data("fatal pdf text")
    assert res_exc.extraction_failed
    assert "API error" in res_exc.extraction_warnings[0]

