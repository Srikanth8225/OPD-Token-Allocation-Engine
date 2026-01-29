"""
Token model
"""
from datetime import datetime, timedelta
from typing import Optional
from config import Config

class Token:
    """Represents a patient token for OPD consultation"""
    
    def __init__(self, patient_id: str, doctor_id: str, slot_id: str,
                 source: str, priority: int, status: str = 'CONFIRMED',
                 token_number: Optional[int] = None, token_id: Optional[str] = None):
        self.id = token_id or f"TKN{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.token_number = token_number
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.slot_id = slot_id
        self.source = source
        self.priority = priority
        self.status = status  # CONFIRMED, WAITLISTED, CANCELLED, NO_SHOW, COMPLETED
        self.estimated_time = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.notes = []  # Track status changes and events
    
    def update_status(self, new_status: str, note: Optional[str] = None):
        """Update token status with timestamp"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        event_note = note or f"Status changed: {old_status} -> {new_status}"
        self.add_note(event_note)
    
    def add_note(self, note: str):
        """Add a timestamped note to token history"""
        self.notes.append({
            'timestamp': datetime.now().isoformat(),
            'note': note
        })
    
    def calculate_estimated_time(self, slot_start_time: str, position_in_queue: int):
        """Calculate estimated consultation time based on queue position"""
        # Parse slot start time
        hour, minute = map(int, slot_start_time.split(':'))
        base_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Add time based on queue position (average consultation time per patient)
        estimated = base_time + timedelta(minutes=(position_in_queue - 1) * Config.AVERAGE_CONSULTATION_MINUTES)
        self.estimated_time = estimated.strftime('%H:%M')
        return self.estimated_time
    
    def to_dict(self):
        """Convert token to dictionary"""
        return {
            'id': self.id,
            'token_number': self.token_number,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'slot_id': self.slot_id,
            'source': self.source,
            'priority': self.priority,
            'status': self.status,
            'estimated_time': self.estimated_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_dict_detailed(self):
        """Convert token to detailed dictionary with history"""
        data = self.to_dict()
        data['notes'] = self.notes
        return data
    
    def __repr__(self):
        return f"<Token {self.id}: #{self.token_number} - {self.status} (Priority: {self.priority})>"
