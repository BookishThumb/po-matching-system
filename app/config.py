# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str = "your_groq_api_key_here"
    groq_model: str = "llama-3.3-70b-versatile"
    database_url: str = "sqlite:///./po_matching.db"
    inbox_watch_folder: str = "./sample_data/emails"
    log_level: str = "INFO"
    discrepancy_tolerance_percent: float = 2.0
    
    # IMAP Configuration
    enable_imap: bool = False
    imap_server: str = ""
    imap_port: int = 993
    imap_user: str = ""
    imap_password: str = ""
    
    # Airtable Configuration
    airtable_api_key: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = "Invoices"

    # Security Configuration
    admin_username: str = "admin"
    admin_password: str = "password" # in a real app, this would be a hash or in a DB
    jwt_secret_key: str = "super_secret_key_please_change"
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
