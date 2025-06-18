from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from app.core.config import settings

class Reservation(Document):
    # Basic Information
    patient_id: Indexed(str)
    doctor_id: Indexed(str) 
    box_id: Indexed(str)
    
    # Appointment Details
    date: Indexed(date)
    start_time: time
    end_time: time
    duration_minutes: int = Field(ge=15, le=480)  # 15 minutes to 8 hours
    
    # Status
    status: str = Field(..., regex=f"^({'|'.join(settings.RESERVATION_STATUS.values())})$")
    
    # Purpose
    appointment_type: str  # "consultation", "procedure", "follow_up", "emergency"
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    # Administrative
    created_by: str  # User ID who created the reservation
    priority: str = "normal"  # "low", "normal", "high", "urgent"
    
    # Patient Information
    patient_name: str
    patient_phone: Optional[str] = None
    patient_email: Optional[str] = None
    
    # Doctor Information  
    doctor_name: str
    doctor_specialization: Optional[str] = None
    
    # Box Information
    box_name: str
    box_location: str
    
    # Confirmation
    confirmation_code: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None
    
    # Check-in/out
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    actual_duration: Optional[int] = None  # in minutes
    
    # Cancellation
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    # Follow-up
    follow_up_required: bool = False
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Reminders
    reminder_sent: bool = False
    reminder_sent_at: Optional[datetime] = None
    
    class Settings:
        name = "reservations"
        indexes = [
            "patient_id",
            "doctor_id",
            "box_id",
            "date",
            "status",
            "appointment_type",
            "created_at"
        ]
    
    def __str__(self):
        return f"Reservation(patient={self.patient_name}, date={self.date}, status={self.status})"
    
    def is_active(self) -> bool:
        """Check if reservation is active"""
        return self.status in [
            settings.RESERVATION_STATUS["PENDING"],
            settings.RESERVATION_STATUS["CONFIRMED"],
            settings.RESERVATION_STATUS["IN_PROGRESS"]
        ]
    
    def can_be_cancelled(self) -> bool:
        """Check if reservation can be cancelled"""
        return self.status in [
            settings.RESERVATION_STATUS["PENDING"],
            settings.RESERVATION_STATUS["CONFIRMED"]
        ]
    
    def can_be_modified(self) -> bool:
        """Check if reservation can be modified"""
        return self.status in [
            settings.RESERVATION_STATUS["PENDING"],
            settings.RESERVATION_STATUS["CONFIRMED"]
        ]
    
    def is_past_due(self) -> bool:
        """Check if reservation is past due"""
        now = datetime.now()
        reservation_datetime = datetime.combine(self.date, self.end_time)
        return reservation_datetime < now and self.status != settings.RESERVATION_STATUS["COMPLETED"]
    
    def get_duration_hours(self) -> float:
        """Get duration in hours"""
        return self.duration_minutes / 60
    
    def get_appointment_datetime(self) -> datetime:
        """Get full appointment datetime"""
        return datetime.combine(self.date, self.start_time)

class ReservationCreate(BaseModel):
    """Schema for creating a reservation"""
    patient_id: str
    doctor_id: str
    box_id: str
    date: date
    start_time: time
    duration_minutes: int = Field(ge=15, le=480)
    appointment_type: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = "normal"

class ReservationUpdate(BaseModel):
    """Schema for updating a reservation"""
    date: Optional[date] = None
    start_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    appointment_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class ReservationStats(BaseModel):
    """Reservation statistics"""
    total_reservations: int
    pending_reservations: int
    confirmed_reservations: int
    completed_reservations: int
    cancelled_reservations: int
    no_show_rate: float
    average_duration: float
    busiest_hours: List[dict]
    reservations_by_type: dict
    monthly_trends: List[dict]