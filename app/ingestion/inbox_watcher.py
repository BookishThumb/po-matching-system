import os
import time
import json
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from app.config import settings
from app.utils.logger import logger

class EmailPayload(BaseModel):
    folder_path: str
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    received_at: Optional[str] = None
    pdf_path: str

def scan_inbox() -> List[EmailPayload]:
    """
    Scans the configured inbox folder for new 'emails' (subfolders).
    Ignores folders that don't contain a PDF or have already been processed.
    """
    inbox_dir = Path(settings.inbox_watch_folder)
    
    if not inbox_dir.exists():
        logger.warning(f"Inbox watch folder does not exist: {inbox_dir}")
        return []

    emails = []
    
    for item in inbox_dir.iterdir():
        if item.is_dir():
            processed_marker = item / ".processed"
            if processed_marker.exists():
                continue
                
            metadata_file = item / "metadata.json"
            metadata = {}
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r") as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to read metadata for {item.name}: {e}")
            
            # Find PDF
            pdf_files = list(item.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"Ignoring email folder '{item.name}' because it contains no PDF attachment.")
                # Mark as processed so we don't keep warning about it
                with open(processed_marker, "w") as f:
                    f.write("ignored: no pdf")
                continue
                
            pdf_path = str(pdf_files[0].absolute())
            
            email = EmailPayload(
                folder_path=str(item.absolute()),
                sender_name=metadata.get("sender_name"),
                sender_email=metadata.get("sender_email"),
                subject=metadata.get("subject"),
                received_at=metadata.get("received_at"),
                pdf_path=pdf_path
            )
            
            emails.append(email)
            logger.info(f"Discovered new email payload: {item.name}", extra={"pdf_path": pdf_path})
            
    return emails

def mark_as_processed(email: EmailPayload):
    """Marks an email folder as processed to prevent reprocessing."""
    folder = Path(email.folder_path)
    marker = folder / ".processed"
    try:
        with open(marker, "w") as f:
            f.write(f"processed at {time.time()}")
    except Exception as e:
        logger.error(f"Failed to mark email {folder.name} as processed: {e}")

def process_new_emails() -> List[EmailPayload]:
    """
    One-shot processing of new emails. 
    This is what the API/demo will call.
    """
    logger.info("Scanning for new emails...")
    emails = scan_inbox()
    logger.info(f"Found {len(emails)} new emails to process.")
    return emails

def poll_inbox(interval_seconds: int = 10):
    """
    Optional polling loop mode (Not the default demo path).
    """
    logger.info(f"Starting inbox polling loop (interval: {interval_seconds}s)")
    try:
        while True:
            process_new_emails()
            # Actual processing would be hooked up here
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        logger.info("Polling loop stopped.")
