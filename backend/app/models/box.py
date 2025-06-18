from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.core.config import settings

class Box(Document):
    # Basic Information
    name: Indexed(str, unique=True)
    description: Optional[str] = None
    location: str
    
    # Capacity and Equipment
    capacity: int = Field(ge=1, le=10)  # Between 1 and 10 people
    equipment: Optional[List[str]] = []
    
    # Status
    status: str = Field(..., regex=f"^({'|'.join(settings.BOX_STATUS.values())})$")
    
    # Availability
    is_active: bool = True
    available_from: Optional[str] = "08:00"  # Format: HH:MM
    available_to: Optional[str] = "18:00"    # Format: HH:MM
    available_days: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    # Additional Information
    floor: Optional[int] = None
    room_number: Optional[str] = None
    special_requirements: Optional[List[str]] = []
    
    # Current Assignment
    current_reservation_id: Optional[str] = None
    current_doctor_id: Optional[str] = None
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Maintenance
    last_maintenance: Optional[datetime] = None
    maintenance_notes: Optional[str] = None
    
    class Settings:
        name = "boxes"
        indexes = [
            "name",
            "status",
            "location",
            "is_active"
        ]
    
    def __str__(self):
        return f"Box(name={self.name}, status={self.status})"
    
    def is_available(self) -> bool:
        """Check if box is available for booking"""
        return (
            self.is_active and 
            self.status == settings.BOX_STATUS["AVAILABLE"] and
            self.current_reservation_id is None
        )
    
    def is_occupied(self) -> bool:
        """Check if box is currently occupied"""
        return self.status == settings.BOX_STATUS["OCCUPIED"]
    
    def is_in_maintenance(self) -> bool:
        """Check if box is in maintenance"""
        return self.status == settings.BOX_STATUS["MAINTENANCE"]
    
    def get_availability_info(self) -> dict:
        """Get box availability information"""
        return {
            "is_available": self.is_available(),
            "status": self.status,
            "available_from": self.available_from,
            "available_to": self.available_to,
            "available_days": self.available_days,
            "current_reservation": self.current_reservation_id,
            "current_doctor": self.current_doctor_id
        }

class BoxCreate(BaseModel):
    """Schema for creating a box"""
    name: str
    description: Optional[str] = None
    location: str
    capacity: int = Field(ge=1, le=10)
    equipment: Optional[List[str]] = []
    available_from: Optional[str] = "08:00"
    available_to: Optional[str] = "18:00"
    available_days: Optional[List[str]] = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    floor: Optional[int] = None
    room_number: Optional[str] = None
    special_requirements: Optional[List[str]] = []

class BoxUpdate(BaseModel):
    """Schema for updating a box"""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1, le=10)
    equipment: Optional[List[str]] = None
    status: Optional[str] = None
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    available_days: Optional[List[str]] = None
    floor: Optional[int] = None
    room_number: Optional[str] = None
    special_requirements: Optional[List[str]] = None
    maintenance_notes: Optional[str] = None

class BoxStats(BaseModel):
    """Box statistics"""
    total_boxes: int
    available_boxes: int
    occupied_boxes: int
    maintenance_boxes: int
    utilization_rate: float
    boxes_by_floor: dict
    most_used_boxes: List[dict]