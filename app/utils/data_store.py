"""
In-memory data store for application state
"""
from typing import Dict, Optional
from app.models import Doctor, TimeSlot, Token, Patient

class DataStore:
    """Singleton data store for all application data"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize empty data structures"""
        self.doctors: Dict[str, Doctor] = {}
        self.time_slots: Dict[str, TimeSlot] = {}
        self.tokens: Dict[str, Token] = {}
        self.patients: Dict[str, Patient] = {}
    
    # Doctor operations
    def add_doctor(self, doctor: Doctor) -> Doctor:
        """Add a doctor to the store"""
        self.doctors[doctor.id] = doctor
        return doctor
    
    def get_doctor(self, doctor_id: str) -> Optional[Doctor]:
        """Get a doctor by ID"""
        return self.doctors.get(doctor_id)
    
    def get_all_doctors(self) -> list:
        """Get all doctors"""
        return list(self.doctors.values())
    
    # Time slot operations
    def add_time_slot(self, slot: TimeSlot) -> TimeSlot:
        """Add a time slot to the store"""
        self.time_slots[slot.id] = slot
        # Also add to doctor's slots
        doctor = self.get_doctor(slot.doctor_id)
        if doctor:
            doctor.add_slot(slot)
        return slot
    
    def get_time_slot(self, slot_id: str) -> Optional[TimeSlot]:
        """Get a time slot by ID"""
        return self.time_slots.get(slot_id)
    
    def get_slots_by_doctor(self, doctor_id: str, date: Optional[str] = None) -> list:
        """Get all slots for a doctor, optionally filtered by date"""
        slots = [slot for slot in self.time_slots.values() if slot.doctor_id == doctor_id]
        if date:
            slots = [slot for slot in slots if slot.date == date]
        return slots
    
    def find_slot_by_time(self, doctor_id: str, date: str, start_time: str) -> Optional[TimeSlot]:
        """Find a specific slot by doctor, date, and time"""
        for slot in self.time_slots.values():
            if (slot.doctor_id == doctor_id and 
                slot.date == date and 
                slot.start_time == start_time):
                return slot
        return None
    
    # Token operations
    def add_token(self, token: Token) -> Token:
        """Add a token to the store"""
        self.tokens[token.id] = token
        return token
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """Get a token by ID"""
        return self.tokens.get(token_id)
    
    def get_tokens_by_slot(self, slot_id: str) -> list:
        """Get all tokens for a slot"""
        return [token for token in self.tokens.values() if token.slot_id == slot_id]
    
    def get_tokens_by_patient(self, patient_id: str) -> list:
        """Get all tokens for a patient"""
        return [token for token in self.tokens.values() if token.patient_id == patient_id]
    
    # Patient operations
    def add_patient(self, patient: Patient) -> Patient:
        """Add a patient to the store"""
        self.patients[patient.id] = patient
        return patient
    
    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID"""
        return self.patients.get(patient_id)
    
    def find_patient_by_phone(self, phone: str) -> Optional[Patient]:
        """Find a patient by phone number"""
        for patient in self.patients.values():
            if patient.phone == phone:
                return patient
        return None
    
    # Utility methods
    def clear_all(self):
        """Clear all data (useful for testing)"""
        self._initialize()
    
    def get_stats(self) -> dict:
        """Get overall statistics"""
        return {
            'total_doctors': len(self.doctors),
            'total_slots': len(self.time_slots),
            'total_tokens': len(self.tokens),
            'total_patients': len(self.patients),
            'confirmed_tokens': len([t for t in self.tokens.values() if t.status == 'CONFIRMED']),
            'waitlisted_tokens': len([t for t in self.tokens.values() if t.status == 'WAITLISTED']),
            'cancelled_tokens': len([t for t in self.tokens.values() if t.status == 'CANCELLED']),
            'no_show_tokens': len([t for t in self.tokens.values() if t.status == 'NO_SHOW'])
        }

# Global instance
db = DataStore()
