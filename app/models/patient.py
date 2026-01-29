"""
Data models for OPD Token Allocation Engine
"""
from datetime import datetime
from typing import Optional

class Patient:
    """Represents a patient in the system"""
    
    def __init__(self, name: str, phone: str, age: int, gender: str, 
                 patient_id: Optional[str] = None, medical_record_number: Optional[str] = None):
        self.id = patient_id or f"PAT{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.name = name
        self.phone = phone
        self.age = age
        self.gender = gender
        self.medical_record_number = medical_record_number or f"MRN{self.id}"
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert patient to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'age': self.age,
            'gender': self.gender,
            'medical_record_number': self.medical_record_number
        }
    
    def __repr__(self):
        return f"<Patient {self.id}: {self.name}>"
