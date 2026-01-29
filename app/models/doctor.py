"""
Doctor model
"""
from typing import Optional

class Doctor:
    """Represents a doctor in the OPD system"""
    
    def __init__(self, name: str, specialization: str, 
                 doctor_id: Optional[str] = None, active: bool = True):
        self.id = doctor_id or f"DOC{len(name.replace(' ', ''))}{hash(name) % 1000:03d}"
        self.name = name
        self.specialization = specialization
        self.active = active
        self.slots = []  # List of TimeSlot objects
    
    def add_slot(self, slot):
        """Add a time slot to this doctor"""
        self.slots.append(slot)
    
    def to_dict(self):
        """Convert doctor to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'specialization': self.specialization,
            'active': self.active,
            'total_slots': len(self.slots)
        }
    
    def __repr__(self):
        return f"<Doctor {self.id}: {self.name} - {self.specialization}>"
