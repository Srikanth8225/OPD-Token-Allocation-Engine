"""
Allocation Service - Core token allocation logic
"""
from typing import Optional, Dict, Tuple
from datetime import datetime
from app.models import Token, Patient, TimeSlot
from app.core import PriorityManager, QueueManager
from app.utils.data_store import db
from config import Config

class AllocationService:
    """Handles token allocation logic"""
    
    def __init__(self):
        self.priority_manager = PriorityManager()
        self.queue_manager = QueueManager()
    
    def allocate_token(self, patient_data: dict, doctor_id: str, 
                      date: str, preferred_slot_time: str, source: str) -> Tuple[Token, str]:
        """
        Allocate a token for a patient
        
        Args:
            patient_data: Patient information (name, phone, age, gender)
            doctor_id: Doctor ID
            date: Date for appointment (YYYY-MM-DD)
            preferred_slot_time: Preferred start time (HH:MM)
            source: Token source type
            
        Returns:
            Tuple of (Token object, status_message)
        """
        # Validate inputs
        if not self.priority_manager.validate_source(source):
            raise ValueError(f"Invalid source type: {source}")
        
        doctor = db.get_doctor(doctor_id)
        if not doctor:
            raise ValueError(f"Doctor not found: {doctor_id}")
        
        # Get or create patient
        patient = db.find_patient_by_phone(patient_data['phone'])
        if not patient:
            patient = Patient(
                name=patient_data['name'],
                phone=patient_data['phone'],
                age=patient_data['age'],
                gender=patient_data['gender']
            )
            db.add_patient(patient)
        
        # Find the requested time slot
        slot = db.find_slot_by_time(doctor_id, date, preferred_slot_time)
        if not slot:
            raise ValueError(f"Time slot not found: {date} {preferred_slot_time}")
        
        # Get priority for this source
        priority = self.priority_manager.get_priority_for_source(source)
        
        # Try to allocate token
        if not slot.is_full:
            # Slot has capacity - allocate directly
            token = self._create_confirmed_token(patient.id, doctor_id, slot, source, priority)
            slot.add_token(token.id)
            db.add_token(token)
            
            return token, "CONFIRMED"
        
        else:
            # Slot is full - add to waitlist
            token = self._create_waitlisted_token(patient.id, doctor_id, slot, source, priority)
            slot.add_to_waitlist(token.id)
            db.add_token(token)
            
            # Add to queue manager for priority tracking
            position = self.queue_manager.add_to_waitlist(slot.id, token.id, priority)
            
            return token, f"WAITLISTED (Position: {position})"
    
    def _create_confirmed_token(self, patient_id: str, doctor_id: str, 
                               slot: TimeSlot, source: str, priority: int) -> Token:
        """Create a confirmed token"""
        # Calculate token number (position in queue)
        token_number = slot.allocated_count + 1
        
        token = Token(
            patient_id=patient_id,
            doctor_id=doctor_id,
            slot_id=slot.id,
            source=source,
            priority=priority,
            status='CONFIRMED',
            token_number=token_number
        )
        
        # Calculate estimated time
        token.calculate_estimated_time(slot.start_time, token_number)
        token.add_note(f"Token allocated from {source}")
        
        return token
    
    def _create_waitlisted_token(self, patient_id: str, doctor_id: str,
                                slot: TimeSlot, source: str, priority: int) -> Token:
        """Create a waitlisted token"""
        token = Token(
            patient_id=patient_id,
            doctor_id=doctor_id,
            slot_id=slot.id,
            source=source,
            priority=priority,
            status='WAITLISTED',
            token_number=None  # Will be assigned when promoted
        )
        
        token.add_note(f"Added to waitlist from {source}")
        
        return token
    
    def allocate_emergency_token(self, patient_data: dict, doctor_id: str,
                                date: str, preferred_slot_time: str) -> Tuple[Token, str]:
        """
        Allocate an emergency token with highest priority
        
        This may demote an existing lower-priority token if slot is full
        
        Returns:
            Tuple of (Token object, status_message)
        """
        # Get or create patient
        patient = db.find_patient_by_phone(patient_data['phone'])
        if not patient:
            patient = Patient(
                name=patient_data['name'],
                phone=patient_data['phone'],
                age=patient_data['age'],
                gender=patient_data['gender']
            )
            db.add_patient(patient)
        
        # Find the requested time slot
        slot = db.find_slot_by_time(doctor_id, date, preferred_slot_time)
        if not slot:
            raise ValueError(f"Time slot not found: {date} {preferred_slot_time}")
        
        emergency_priority = self.priority_manager.get_priority_for_source('EMERGENCY')
        
        # If slot has capacity, allocate directly
        if not slot.is_full:
            token = self._create_confirmed_token(patient.id, doctor_id, slot, 'EMERGENCY', emergency_priority)
            slot.add_token(token.id)
            db.add_token(token)
            return token, "EMERGENCY - CONFIRMED"
        
        # Slot is full - find lowest priority token to demote
        confirmed_tokens = [db.get_token(tid) for tid in slot.tokens]
        
        # Find token with lowest priority (highest priority number)
        lowest_priority_token = max(confirmed_tokens, key=lambda t: t.priority)
        
        # Check if we should demote
        if self.priority_manager.should_demote(lowest_priority_token.priority, emergency_priority):
            # Demote the lowest priority token
            from app.services.reallocation_service import ReallocationService
            realloc_service = ReallocationService()
            realloc_service.demote_token(lowest_priority_token.id)
            
            # Now allocate the emergency token
            token = self._create_confirmed_token(patient.id, doctor_id, slot, 'EMERGENCY', emergency_priority)
            slot.add_token(token.id)
            db.add_token(token)
            
            return token, f"EMERGENCY - CONFIRMED (Demoted token {lowest_priority_token.id})"
        
        else:
            # Even emergency can't bump anyone (shouldn't happen with proper priority setup)
            token = self._create_waitlisted_token(patient.id, doctor_id, slot, 'EMERGENCY', emergency_priority)
            slot.add_to_waitlist(token.id)
            db.add_token(token)
            position = self.queue_manager.add_to_waitlist(slot.id, token.id, emergency_priority)
            
            return token, f"EMERGENCY - WAITLISTED (Position: {position})"
    
    def get_slot_status(self, slot_id: str) -> dict:
        """Get detailed status of a time slot"""
        slot = db.get_time_slot(slot_id)
        if not slot:
            raise ValueError(f"Slot not found: {slot_id}")
        
        doctor = db.get_doctor(slot.doctor_id)
        
        confirmed_tokens = [db.get_token(tid) for tid in slot.tokens if db.get_token(tid)]
        waitlisted_tokens = [db.get_token(tid) for tid in slot.waitlist if db.get_token(tid)]
        
        return {
            'slot_id': slot.id,
            'doctor_name': doctor.name if doctor else 'Unknown',
            'doctor_id': slot.doctor_id,
            'time': f"{slot.start_time} - {slot.end_time}",
            'date': slot.date,
            'max_capacity': slot.max_capacity,
            'allocated': slot.allocated_count,
            'available': slot.available_count,
            'waitlist_count': len(waitlisted_tokens),
            'confirmed_tokens': [
                {
                    'token_id': t.id,
                    'token_number': t.token_number,
                    'patient_name': db.get_patient(t.patient_id).name if db.get_patient(t.patient_id) else 'Unknown',
                    'source': t.source,
                    'priority': t.priority,
                    'estimated_time': t.estimated_time
                }
                for t in confirmed_tokens
            ],
            'waitlisted_tokens': [
                {
                    'token_id': t.id,
                    'patient_name': db.get_patient(t.patient_id).name if db.get_patient(t.patient_id) else 'Unknown',
                    'source': t.source,
                    'priority': t.priority,
                    'waitlist_position': self.queue_manager.get_waitlist_position(slot.id, t.id)
                }
                for t in waitlisted_tokens
            ]
        }
