import os
import imaplib
import email
import json
import time
from email.header import decode_header
from email.utils import parsedate_to_datetime
from pathlib import Path
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def decode_mime_header(header_value):
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                result += part.decode(encoding or "utf-8")
            except (LookupError, UnicodeDecodeError):
                result += part.decode("utf-8", errors="ignore")
        else:
            result += part
    return result

def extract_email_address(from_header):
    if not from_header:
        return "", ""
    # "Name" <email@example.com> or just email@example.com
    from_header = decode_mime_header(from_header)
    if "<" in from_header and ">" in from_header:
        name, addr = from_header.split("<", 1)
        addr = addr.split(">")[0].strip()
        name = name.strip(' "')
        return name, addr
    return "", from_header.strip()

def fetch_unread_emails():
    """
    Connects to IMAP, finds unread emails with PDFs, and saves them to the watch folder.
    """
    if not settings.enable_imap:
        logger.info("IMAP is disabled in settings. Skipping email fetch.")
        return

    try:
        logger.info(f"Connecting to IMAP server: {settings.imap_server}:{settings.imap_port}")
        mail = imaplib.IMAP4_SSL(settings.imap_server, settings.imap_port)
        mail.login(settings.imap_user, settings.imap_password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            logger.info("No new unread emails found.")
            mail.logout()
            return

        email_ids = messages[0].split()
        
        # Limit to the most recent 1 unread email for testing purposes
        max_emails = 1
        if len(email_ids) > max_emails:
            logger.info(f"Limiting to the {max_emails} most recent emails out of {len(email_ids)} unread.")
            email_ids = email_ids[-max_emails:]
        else:
            logger.info(f"Found {len(email_ids)} unread emails.")

        watch_dir = Path(settings.inbox_watch_folder)
        watch_dir.mkdir(parents=True, exist_ok=True)

        for email_id in email_ids:
            # PEEK prevents the email from automatically being marked as 'read'
            status, msg_data = mail.fetch(email_id, "(BODY.PEEK[])")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = decode_mime_header(msg.get("Subject", ""))
                    from_header = msg.get("From", "")
                    sender_name, sender_email = extract_email_address(from_header)
                    date_header = msg.get("Date")
                    received_at = ""
                    if date_header:
                        try:
                            dt = parsedate_to_datetime(date_header)
                            received_at = dt.isoformat()
                        except Exception:
                            received_at = str(date_header)

                    logger.info(f"Processing email from {sender_email} - Subject: {subject}")

                    has_pdf = False
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_maintype() == "multipart":
                                continue
                            if part.get("Content-Disposition") is None:
                                continue

                            filename = part.get_filename()
                            if filename:
                                filename = decode_mime_header(filename)
                                if filename.lower().endswith(".pdf"):
                                    # Create folder for this email
                                    folder_name = f"imap_{int(time.time())}_{email_id.decode('utf-8')}"
                                    folder_path = watch_dir / folder_name
                                    folder_path.mkdir(parents=True, exist_ok=True)

                                    # Save PDF
                                    pdf_path = folder_path / "invoice.pdf"
                                    with open(pdf_path, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                        
                                    # Save Metadata
                                    metadata = {
                                        "sender_name": sender_name,
                                        "sender_email": sender_email,
                                        "subject": subject,
                                        "received_at": received_at
                                    }
                                    with open(folder_path / "metadata.json", "w") as f:
                                        json.dump(metadata, f, indent=2)

                                    has_pdf = True
                                    logger.info(f"Saved PDF from IMAP to {folder_path}")
                                    break # Only save the first PDF
                    
                    if has_pdf:
                        # Explicitly mark as read ONLY if we successfully extracted a PDF
                        mail.store(email_id, '+FLAGS', '\\Seen')
                        logger.info(f"Marked email {email_id.decode('utf-8')} as read.")
                    else:
                        logger.info(f"No PDF found in email {email_id.decode('utf-8')}. Leaving as unread.")
                        
        mail.logout()

    except Exception as e:
        logger.error(f"Error fetching emails via IMAP: {e}")
