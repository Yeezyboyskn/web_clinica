from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RedSalud API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str = "mongodb://admin:password123@localhost:27017/redsalud_db?authSource=admin"
    DATABASE_NAME: str = "redsalud_db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_FOLDER: str = "uploads"
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Roles
    USER_ROLES = {
        "ADMIN": "admin",
        "DOCTOR": "doctor", 
        "PATIENT": "patient"
    }
    
    # Box Status
    BOX_STATUS = {
        "AVAILABLE": "available",
        "OCCUPIED": "occupied",
        "MAINTENANCE": "maintenance",
        "RESERVED": "reserved"
    }
    
    # Reservation Status
    RESERVATION_STATUS = {
        "PENDING": "pending",
        "CONFIRMED": "confirmed",
        "IN_PROGRESS": "in_progress",
        "COMPLETED": "completed",
        "CANCELLED": "cancelled",
        "NO_SHOW": "no_show"
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        settings.UPLOAD_FOLDER,
        "logs",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Call on import
create_directories()