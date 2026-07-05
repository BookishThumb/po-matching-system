import json
from app.ai.groq_client import call_groq, GroqAPIError
from app.ai.extraction_prompt import INVOICE_EXTRACTION_SYSTEM_PROMPT
from app.schemas.invoice_schema import InvoiceExtractionResult
from app.utils.logger import logger

def extract_invoice_data(pdf_text: str) -> InvoiceExtractionResult:
    """
    Orchestrates the Groq LLM extraction from PDF text to a validated Pydantic model.
    """
    logger.info("Starting AI extraction of invoice data")
    
    user_prompt = f"Here is the text extracted from the invoice PDF:\n\n{pdf_text}"
    
    # Attempt 1
    try:
        raw_response = call_groq(INVOICE_EXTRACTION_SYSTEM_PROMPT, user_prompt)
        parsed_json = json.loads(raw_response)
        result = InvoiceExtractionResult(**parsed_json)
        logger.info("AI extraction successful on first attempt")
        return result
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse or validate initial LLM response: {str(e)}", extra={"raw_response": raw_response if 'raw_response' in locals() else None})
        
        # Attempt 2 (Retry with correction)
        correction_prompt = user_prompt + "\n\nYour previous response was not valid JSON or failed schema validation. Return ONLY valid JSON matching the exact schema."
        try:
            logger.info("Retrying AI extraction with correction prompt")
            raw_response_2 = call_groq(INVOICE_EXTRACTION_SYSTEM_PROMPT, correction_prompt)
            parsed_json_2 = json.loads(raw_response_2)
            result_2 = InvoiceExtractionResult(**parsed_json_2)
            logger.info("AI extraction successful on retry")
            return result_2
        except Exception as e2:
            logger.error(f"AI extraction failed completely after retry: {str(e2)}", extra={"raw_response": raw_response_2 if 'raw_response_2' in locals() else None})
            
            # Return a failed result object to be handled by downstream manual review
            return InvoiceExtractionResult(
                extraction_failed=True,
                extraction_warnings=[f"Fatal extraction error: {str(e2)}"]
            )
    except GroqAPIError as api_err:
        logger.error(f"Groq API error during extraction: {str(api_err)}")
        return InvoiceExtractionResult(
            extraction_failed=True,
            extraction_warnings=[f"API error: {str(api_err)}"]
        )
