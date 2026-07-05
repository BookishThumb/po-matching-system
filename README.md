# Invoice PO Guardian

An AI-powered procurement automation pipeline that ingests invoice PDFs, extracts structured data using Llama-3 (via Groq), and automatically validates them against stored Purchase Orders (POs) based on configurable tolerance thresholds.

## Architecture Overview

```text
[Inbox Watcher] -> [PDF Text Extraction] -> [Groq AI Extraction] -> [PO Retrieval]
                                                                          |
                                                                          v
[Approval/Review UI] <- [Store Record] <- [Validation Rules] <- [Discrepancy Detection] <- [Field Comparison]
```

This system acts as a code-based equivalent to tools like n8n and Airtable, using FastAPI and SQLite to build a standalone processing and review pipeline.

## Setup Instructions

1. Clone or open the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows: .\venv\Scripts\Activate
   # Mac/Linux: source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` to `.env` and fill in your actual `GROQ_API_KEY`.
5. Seed the database with the sample POs:
   ```bash
   python -m app.db.seed
   ```
6. Generate the sample PDF invoices (optional, script already ran during generation):
   ```bash
   python scripts/generate_sample_invoices.py
   ```
7. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
8. Open your browser to `http://localhost:8000` to view the Procurement Review UI.

## Required Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (required for LLM extraction). |
| `GROQ_MODEL` | The LLM model to use (default: `llama-3.3-70b-versatile`). |
| `DATABASE_URL` | SQLite database URI (default: `sqlite:///./po_matching.db`). |
| `INBOX_WATCH_FOLDER` | Path to monitor for incoming emails (default: `./sample_data/emails`). |
| `LOG_LEVEL` | Application logging level (default: `INFO`). |
| `DISCREPANCY_TOLERANCE_PERCENT` | Numeric tolerance for amount matching (default: `2.0`). |

## Workflow Explanation

1. **Ingestion:** `app/ingestion/inbox_watcher.py` simulates an email inbox, passing new folders (containing metadata + PDF) to the pipeline.
2. **Extraction:** `app/ingestion/pdf_extractor.py` reads the PDF text. `app/ai/extractor.py` sends the text to Groq and parses the JSON back into a Pydantic schema.
3. **Matching Engine:** `app/matching/po_matcher.py` pulls the PO from SQLite and compares it field-by-field (amounts, line items).
4. **Discrepancies:** `app/matching/discrepancy.py` analyzes the match to flag deviations (e.g. quantity mismatches, price mismatches, missing PO).
5. **Business Rules:** `app/matching/validation_rules.py` triages the invoice into `Ready for Payment`, `Procurement Review`, or `Rejected`.
6. **Storage:** The full `Invoice` is saved in SQLite, and an `AuditLog` entry is appended.

## How to Run the Demo

1. Make sure your server is running (`uvicorn app.main:app`).
2. Open another terminal and run the demo script:
   ```bash
   python scripts/run_demo.py
   ```
   *This script triggers the `POST /ingest` endpoint to process all 7 sample emails, and also tests the `POST /ingest/simulate-failure` endpoint.*
3. Open `http://localhost:8000` in your browser.
4. You will see the list of processed invoices. Use the dropdown to filter by status. Click "View" to see the extracted data side-by-side with the PO, discrepancy badges, and full audit logs.

## Business Rules Documentation

The final status of an invoice is determined by `validation_rules.py` based on discrepancies:
- **No discrepancies:** `Ready for Payment`
- **Only minor discrepancies:** `Procurement Review`
- **Any major discrepancy (or missing PO):** `Rejected`

Discrepancy Severity Thresholds (defined in `discrepancy.py`):
- **Vendor Name mismatch:** Major
- **Missing PO:** Major
- **Missing Line Items (on invoice):** Major
- **Extra Line Items (on invoice):** Minor (assumed to be shipping/handling)
- **Quantity Mismatch:** Minor if difference < 10%, Major if >= 10%
- **Unit Price Mismatch:** Minor if difference < 10%, Major if >= 10%
- **Invoice Total Exceeds PO:** Minor if difference < 10%, Major if >= 10%

## Assumptions Made

- **No live email inbox connected:** Ingestion is simulated via a watched folder (`sample_data/emails`).
- **SQLite Database:** Used as the local equivalent of Airtable/Notion (per the "or equivalent" spec allowance).
- **FastAPI / Python Orchestration:** Substituted for n8n. The pipeline graph is provided in `workflow_export.json`.
- **Fuzzy Matching:** Line item matching uses description similarity rather than strict equality since real-world vendor invoices often reword PO line items slightly.
- **Log file paths:** Application logs are written to `app.log` in the project root to support the `GET /logs/recent` frontend view.

## Known Limitations

- The PDF extractor (`pdfplumber`) relies on text layers. It will not work on scanned image-only PDFs without an OCR layer. (Such failures are caught and flagged for human review).
- No currency conversion is performed. If an invoice is in GBP but the PO is in USD, it is simply flagged as a discrepancy.

## AI Prompts Used

The following system prompt is used by the Groq extraction node (`app/ai/extraction_prompt.py`):

```text
You are an expert invoice data extraction system. Your task is to extract precise, structured data from the provided text of an invoice PDF.

Return ONLY valid JSON. No markdown, no commentary, no code fences.

The JSON output MUST exactly match the following structure:
{
  "vendor_name": "string or null",
  "vendor_id": "string or null",
  "purchase_order_number": "string or null",
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD string or null",
  "due_date": "YYYY-MM-DD string or null",
  "currency": "3-letter currency code string or null",
  "net_amount": float or null,
  "tax_amount": float or null,
  "gross_amount": float or null,
  "line_items": [
    {
      "description": "string or null",
      "quantity": float or null,
      "unit_price": float or null,
      "total": float or null
    }
  ],
  "confidence_score": float (0.0 to 1.0),
  "extraction_warnings": ["string explaining any issues or missing fields"]
}

Instructions:
1. If a field cannot be found, use `null` (or empty list `[]` for line_items) and add a note to `extraction_warnings` rather than guessing.
2. Ensure numeric amounts are floats without currency symbols or commas.
3. The `confidence_score` should reflect how certain the extraction is overall (e.g., lower if the PDF text was messy, blurry, or important fields were missing).
4. Dates should be formatted as YYYY-MM-DD if possible.

Example Input (Invoice Text):
INVOICE #10293
Bright Steel Supplies
Date: 2023-10-15
PO Ref: PO-1001

100x Steel rods @ $5.00 = $500.00
500x Bolts @ $0.50 = $250.00

Subtotal: $750.00
Tax: $0.00
Total: $750.00

Example JSON Output:
{
  "vendor_name": "Bright Steel Supplies",
  "vendor_id": null,
  "purchase_order_number": "PO-1001",
  "invoice_number": "10293",
  "invoice_date": "2023-10-15",
  "due_date": null,
  "currency": "USD",
  "net_amount": 750.0,
  "tax_amount": 0.0,
  "gross_amount": 750.0,
  "line_items": [
    {
      "description": "Steel rods",
      "quantity": 100.0,
      "unit_price": 5.0,
      "total": 500.0
    },
    {
      "description": "Bolts",
      "quantity": 500.0,
      "unit_price": 0.5,
      "total": 250.0
    }
  ],
  "confidence_score": 0.95,
  "extraction_warnings": [
    "vendor_id not found",
    "due_date not found"
  ]
}
```
