"""
TimeSlot model
"""
from datetime import datetime, timedelta
from typing import Optional, List
from config import Config

class TimeSlot:
    """Represents a time slot for a doctor"""
    
    def __init__(self, doctor_id: str, start_time: str, end_time: str, 
                 date: str, max_capacity: int = Config.DEFAULT_SLOT_CAPACITY,
                 slot_id: Optional[str] = None):
        self.id = slot_id or f"SLOT{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.date = date  # Format: YYYY-MM-DD
        self.max_capacity = max_capacity
        self.allocated_count = 0
        self.tokens = []  # List of token IDs (confirmed)
        self.waitlist = []  # List of token IDs (waitlisted)
        self.created_at = datetime.now()
    
    @property
    def available_count(self):
        """Calculate available capacity"""
        return self.max_capacity - self.allocated_count
    
    @property
    def is_full(self):
        """Check if slot is at max capacity"""
        return self.allocated_count >= self.max_capacity
    
    @property
    def datetime_str(self):
        """Get full datetime string"""
        return f"{self.date} {self.start_time}"
    
    def add_token(self, token_id: str):
        """Add a confirmed token to this slot"""
        if self.allocated_count < self.max_capacity:
            self.tokens.append(token_id)
            self.allocated_count += 1
            return True
        return False
    
    def remove_token(self, token_id: str):
        """Remove a token from this slot (frees capacity)"""
        if token_id in self.tokens:
            self.tokens.remove(token_id)
            self.allocated_count -= 1
            return True
        return False
    
    def add_to_waitlist(self, token_id: str):
        """Add a token to the waitlist"""
        if token_id not in self.waitlist:
            self.waitlist.append(token_id)
            return True
        return False
    
    def remove_from_waitlist(self, token_id: str):
        """Remove a token from waitlist"""
        if token_id in self.waitlist:
            self.waitlist.remove(token_id)
            return True
        return False
    
    def to_dict(self):
        """Convert time slot to dictionary"""
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'date': self.date,
            'max_capacity': self.max_capacity,
            'allocated_count': self.allocated_count,
            'available_count': self.available_count,
            'is_full': self.is_full,
            'confirmed_tokens': len(self.tokens),
            'waitlisted_tokens': len(self.waitlist)
        }
    
    def __repr__(self):
        return f"<TimeSlot {self.id}: {self.date} {self.start_time}-{self.end_time} ({self.allocated_count}/{self.max_capacity})>"
