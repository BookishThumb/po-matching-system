import logging
import json
import sys
import os
from app.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage()
        }
        
        if hasattr(record, "invoice_id"):
            log_record["invoice_id"] = record.invoice_id
            
        if hasattr(record, "latency_sec"):
            log_record["duration_ms"] = round(record.latency_sec * 1000)
            
        for key, val in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread", "threadName", "processName", "process", "taskName", "invoice_id", "latency_sec", "duration_ms"]:
                log_record[key] = val
                
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if logger already exists
    if not logger.handlers:
        formatter = JSONFormatter()
        
        # Stream handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
        # File handler (for /logs/recent endpoint)
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Set level from config
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
    return logger

logger = setup_logger("po_matching")
