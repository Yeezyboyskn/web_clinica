from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.core.config import settings

class User(Document):
    # Basic Info
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: str
    hashed_password: str
    
    # Role and permissions
    role: str = Field(..., regex=f"^({'|'.join(settings.USER_ROLES.values())})$")
    is_active: bool = True
    is_verified: bool = False
    
    # Personal Information
    rut: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None  # Format: YYYY-MM-DD
    
    # Professional Information (for doctors)
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    
    # Medical Information (for patients)
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Settings
    preferences: Optional[dict] = {}
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username", 
            "role",
            "is_active"
        ]
    
    def __str__(self):
        return f"User(email={self.email}, role={self.role})"
    
    def is_admin(self) -> bool:
        return self.role == settings.USER_ROLES["ADMIN"]
    
    def is_doctor(self) -> bool:
        return self.role == settings.USER_ROLES["DOCTOR"]
    
    def is_patient(self) -> bool:
        return self.role == settings.USER_ROLES["PATIENT"]
    
    def can_manage_boxes(self) -> bool:
        return self.role in [settings.USER_ROLES["ADMIN"]]
    
    def can_manage_users(self) -> bool:
        return self.role in [settings.USER_ROLES["ADMIN"]]
    
    def can_create_schedules(self) -> bool:
        return self.role in [settings.USER_ROLES["ADMIN"], settings.USER_ROLES["DOCTOR"]]
    
    def can_make_reservations(self) -> bool:
        return self.role in [settings.USER_ROLES["PATIENT"]]
    
    def get_public_profile(self) -> dict:
        """Get public profile information"""
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "role": self.role,
            "specialization": self.specialization,
            "department": self.department,
            "is_active": self.is_active
        }

class UserProfile(BaseModel):
    """User profile for updates"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    preferences: Optional[dict] = None

class UserStats(BaseModel):
    """User statistics"""
    total_users: int
    active_users: int
    users_by_role: dict
    recent_registrations: int
    verified_users: int