import pdfplumber
from pathlib import Path
from app.utils.logger import logger

class PDFExtractionError(Exception):
    """Custom exception for when PDF extraction fails (empty, corrupted, no text layer)."""
    pass

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    Handles multi-page PDFs by concatenating text with page markers.
    Raises PDFExtractionError if the file is unreadable or has no text.
    """
    path = Path(file_path)
    if not path.exists():
        logger.error(f"PDF file not found: {file_path}")
        raise PDFExtractionError(f"File not found: {file_path}")
        
    extracted_text = []
    
    try:
        logger.info(f"Starting PDF extraction for {path.name}")
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                raise PDFExtractionError("PDF has no pages")
                
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(f"--- PAGE {i + 1} ---")
                    extracted_text.append(page_text)
                    
        full_text = "\n".join(extracted_text).strip()
        
        if not full_text:
            logger.error(f"No text extracted from PDF (possibly scanned image without OCR): {file_path}")
            raise PDFExtractionError("PDF contains no extractable text layer.")
            
        logger.info(f"Successfully extracted {len(full_text)} characters from {path.name}")
        return full_text
        
    except PDFExtractionError:
        raise
    except Exception as e:
        logger.error(f"Failed to process PDF {file_path}: {str(e)}")
        raise PDFExtractionError(f"Failed to read PDF: {str(e)}") from e
