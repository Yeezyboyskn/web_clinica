from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date, time
from enum import Enum

class DayOfWeek(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday" 
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class ScheduleType(str, Enum):
    REGULAR = "regular"        # Horario regular semanal
    EXCEPTION = "exception"    # Excepción para un día específico
    VACATION = "vacation"      # Vacaciones
    SICK_LEAVE = "sick_leave" # Licencia médica

class TimeSlot(BaseModel):
    """Time slot within a schedule"""
    start_time: time
    end_time: time
    is_available: bool = True
    appointment_duration: int = 30  # minutes
    break_between: int = 5  # minutes between appointments
    
    def get_available_slots(self) -> List[time]:
        """Get all available appointment slots in this time range"""
        slots = []
        current_time = self.start_time
        
        while current_time < self.end_time:
            slots.append(current_time)
            # Add appointment duration + break
            total_minutes = self.appointment_duration + self.break_between
            hours = total_minutes // 60
            minutes = total_minutes % 60
            
            # Calculate next slot time
            next_hour = current_time.hour + hours + (current_time.minute + minutes) // 60
            next_minute = (current_time.minute + minutes) % 60
            
            if next_hour >= 24:
                break
                
            current_time = time(next_hour, next_minute)
        
        return slots

class Schedule(Document):
    # Basic Information
    doctor_id: Indexed(str)
    doctor_name: str
    
    # Schedule Type
    schedule_type: ScheduleType = ScheduleType.REGULAR
    
    # Date Range
    effective_from: date
    effective_to: Optional[date] = None  # None means indefinite
    
    # For regular schedules
    day_of_week: Optional[DayOfWeek] = None
    
    # For specific date exceptions
    specific_date: Optional[date] = None
    
    # Time Slots
    time_slots: List[TimeSlot] = []
    
    # Availability
    is_available: bool = True
    
    # Box Assignment
    preferred_boxes: Optional[List[str]] = []  # Box IDs
    
    # Notes and Restrictions
    notes: Optional[str] = None
    max_patients_per_slot: int = 1
    
    # Break Times
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # Admin or doctor who created this schedule
    
    class Settings:
        name = "schedules"
        indexes = [
            "doctor_id",
            "day_of_week",
            "specific_date",
            "effective_from",
            "schedule_type",
            "is_available"
        ]
    
    def __str__(self):
        return f"Schedule(doctor={self.doctor_name}, type={self.schedule_type})"
    
    def is_active_on(self, check_date: date) -> bool:
        """Check if schedule is active on a specific date"""
        if not self.is_available:
            return False
        
        if check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
        
        if self.schedule_type == ScheduleType.REGULAR:
            # Check day of week
            weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            return self.day_of_week == weekday_names[check_date.weekday()]
        
        elif self.schedule_type == ScheduleType.EXCEPTION:
            return self.specific_date == check_date
        
        return False
    
    def get_available_slots_for_date(self, check_date: date) -> List[time]:
        """Get all available time slots for a specific date"""
        if not self.is_active_on(check_date):
            return []
        
        all_slots = []
        for time_slot in self.time_slots:
            if time_slot.is_available:
                slots = time_slot.get_available_slots()
                all_slots.extend(slots)
        
        return sorted(all_slots)
    
    def has_conflict_with(self, other_schedule: 'Schedule') -> bool:
        """Check if this schedule conflicts with another schedule"""
        if self.doctor_id != other_schedule.doctor_id:
            return False
        
        # Check date overlap
        if self.effective_to and other_schedule.effective_from > self.effective_to:
            return False
        
        if other_schedule.effective_to and self.effective_from > other_schedule.effective_to:
            return False
        
        # Check day/date overlap
        if self.schedule_type == ScheduleType.REGULAR and other_schedule.schedule_type == ScheduleType.REGULAR:
            return self.day_of_week == other_schedule.day_of_week
        
        if self.schedule_type == ScheduleType.EXCEPTION and other_schedule.schedule_type == ScheduleType.EXCEPTION:
            return self.specific_date == other_schedule.specific_date
        
        return True

class ScheduleCreate(BaseModel):
    """Schema for creating a schedule"""
    doctor_id: str
    schedule_type: ScheduleType = ScheduleType.REGULAR
    effective_from: date
    effective_to: Optional[date] = None
    day_of_week: Optional[DayOfWeek] = None
    specific_date: Optional[date] = None
    time_slots: List[TimeSlot]
    preferred_boxes: Optional[List[str]] = []
    notes: Optional[str] = None
    max_patients_per_slot: Optional[int] = 1
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None

class ScheduleUpdate(BaseModel):
    """Schema for updating a schedule"""
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    time_slots: Optional[List[TimeSlot]] = None
    is_available: Optional[bool] = None
    preferred_boxes: Optional[List[str]] = None
    notes: Optional[str] = None
    max_patients_per_slot: Optional[int] = None
    lunch_break_start: Optional[time] = None
    lunch_break_end: Optional[time] = None

class DoctorAvailability(BaseModel):
    """Doctor availability summary"""
    doctor_id: str
    doctor_name: str
    date: date
    available_slots: List[time]
    preferred_boxes: List[str]
    total_slots: int
    booked_slots: int
    availability_percentage: float

class ScheduleStats(BaseModel):
    """Schedule statistics"""
    total_schedules: int
    active_schedules: int
    doctors_with_schedules: int
    average_slots_per_day: float
    busiest_days: List[Dict]
    schedule_coverage: Dict[str, float]