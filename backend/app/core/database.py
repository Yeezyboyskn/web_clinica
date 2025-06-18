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
        "OCCUPIED": "occupied",from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from app.core.config import settings
from app.models.user import User
from app.models.box import Box
from app.models.reservation import Reservation
from app.models.schedule import Schedule

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    """Get database instance"""
    return db.database

async def init_db():
    """Initialize database connection"""
    try:
        # Create motor client
        db.client = AsyncIOMotorClient(settings.DATABASE_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Initialize beanie with models
        await init_beanie(
            database=db.database,
            document_models=[
                User,
                Box, 
                Reservation,
                Schedule
            ]
        )
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create initial data if needed
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_db():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Database connection closed")

async def create_initial_data():
    """Create initial data for development"""
    try:
        # Check if admin user exists
        admin_user = await User.find_one(User.email == "admin@redsalud.cl")
        if not admin_user:
            from app.core.security import get_password_hash
            
            # Create admin user
            admin_user = User(
                email="admin@redsalud.cl",
                username="admin",
                full_name="Administrador Sistema",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
                is_verified=True
            )
            await admin_user.insert()
            logger.info("Admin user created")
        
        # Check if sample boxes exist
        box_count = await Box.count()
        if box_count == 0:
            # Create sample boxes
            sample_boxes = [
                Box(
                    name="Box 1 - Consulta General",
                    description="Box para consultas médicas generales",
                    location="Planta 1 - Ala Norte",
                    capacity=2,
                    equipment=["Camilla", "Escritorio", "Computador"],
                    status="available"
                ),
                Box(
                    name="Box 2 - Cardiología",
                    description="Box especializado en cardiología",
                    location="Planta 2 - Ala Sur", 
                    capacity=3,
                    equipment=["Camilla", "ECG", "Monitor", "Escritorio"],
                    status="available"
                ),
                Box(
                    name="Box 3 - Procedimientos",
                    description="Box para procedimientos menores",
                    location="Planta 1 - Ala Sur",
                    capacity=4,
                    equipment=["Camilla", "Mesa instrumental", "Lámpara", "Monitor"],
                    status="available"
                )
            ]
            
            for box in sample_boxes:
                await box.insert()
            
            logger.info("Sample boxes created")
        
        # Create sample doctor
        doctor_user = await User.find_one(User.email == "doctor@redsalud.cl")
        if not doctor_user:
            from app.core.security import get_password_hash
            
            doctor_user = User(
                email="doctor@redsalud.cl",
                username="doctor1",
                full_name="Dr. Juan Pérez",
                hashed_password=get_password_hash("doctor123"),
                role="doctor",
                is_active=True,
                is_verified=True,
                specialization="Medicina General",
                license_number="12345678"
            )
            await doctor_user.insert()
            logger.info("Sample doctor created")
        
        # Create sample patient
        patient_user = await User.find_one(User.email == "patient@redsalud.cl")
        if not patient_user:
            from app.core.security import get_password_hash
            
            patient_user = User(
                email="patient@redsalud.cl", 
                username="patient1",
                full_name="María González",
                hashed_password=get_password_hash("patient123"),
                role="patient",
                is_active=True,
                is_verified=True,
                rut="12345678-9",
                phone="+56912345678",
                date_of_birth="1990-05-15"
            )
            await patient_user.insert()
            logger.info("Sample patient created")
            
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")

# Database utilities
async def ping_database():
    """Ping database to check connection"""
    try:
        await db.client.admin.command('ping')
        return True
    except Exception:
        return False

async def get_database_stats():
    """Get database statistics"""
    try:
        stats = await db.database.command("dbStats")
        return {
            "database": settings.DATABASE_NAME,
            "collections": stats.get("collections", 0),
            "objects": stats.get("objects", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0)
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return None
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