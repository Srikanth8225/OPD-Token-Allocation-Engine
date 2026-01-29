"""
Reallocation Service - Handles dynamic token reallocation
"""
from typing import Optional
from app.models import Token
from app.core import QueueManager
from app.utils.data_store import db

class ReallocationService:
    """Handles token reallocation on cancellations, no-shows, and demotions"""
    
    def __init__(self):
        self.queue_manager = QueueManager()
    
    def cancel_token(self, token_id: str) -> dict:
        """
        Cancel a token and promote from waitlist if available
        
        Returns:
            Dictionary with cancellation details and promotion info
        """
        token = db.get_token(token_id)
        if not token:
            raise ValueError(f"Token not found: {token_id}")
        
        if token.status in ['CANCELLED', 'COMPLETED', 'NO_SHOW']:
            raise ValueError(f"Cannot cancel token with status: {token.status}")
        
        slot = db.get_time_slot(token.slot_id)
        if not slot:
            raise ValueError(f"Slot not found: {token.slot_id}")
        
        result = {
            'cancelled_token_id': token_id,
            'promoted_token_id': None,
            'message': ''
        }
        
        # Handle based on current status
        if token.status == 'CONFIRMED':
            # Remove from slot and free capacity
            slot.remove_token(token_id)
            token.update_status('CANCELLED', 'Token cancelled by patient/admin')
            
            # Try to promote from waitlist
            promoted_token_id = self._promote_from_waitlist(slot.id)
            if promoted_token_id:
                result['promoted_token_id'] = promoted_token_id
                result['message'] = f"Token cancelled. Token {promoted_token_id} promoted from waitlist."
            else:
                result['message'] = "Token cancelled. No waitlist available."
        
        elif token.status == 'WAITLISTED':
            # Just remove from waitlist
            slot.remove_from_waitlist(token_id)
            self.queue_manager.remove_from_waitlist(slot.id, token_id)
            token.update_status('CANCELLED', 'Waitlisted token cancelled')
            result['message'] = "Waitlisted token cancelled."
        
        return result
    
    def mark_no_show(self, token_id: str) -> dict:
        """
        Mark a token as no-show and promote from waitlist
        
        Returns:
            Dictionary with no-show details and promotion info
        """
        token = db.get_token(token_id)
        if not token:
            raise ValueError(f"Token not found: {token_id}")
        
        if token.status != 'CONFIRMED':
            raise ValueError(f"Only confirmed tokens can be marked as no-show. Current status: {token.status}")
        
        slot = db.get_time_slot(token.slot_id)
        if not slot:
            raise ValueError(f"Slot not found: {token.slot_id}")
        
        # Remove from slot and free capacity
        slot.remove_token(token_id)
        token.update_status('NO_SHOW', 'Patient did not arrive')
        
        result = {
            'no_show_token_id': token_id,
            'promoted_token_id': None,
            'message': ''
        }
        
        # Try to promote from waitlist
        promoted_token_id = self._promote_from_waitlist(slot.id)
        if promoted_token_id:
            result['promoted_token_id'] = promoted_token_id
            result['message'] = f"Token marked no-show. Token {promoted_token_id} promoted from waitlist."
        else:
            result['message'] = "Token marked no-show. No waitlist available."
        
        return result
    
    def demote_token(self, token_id: str) -> dict:
        """
        Demote a confirmed token to waitlist (used for emergency insertions)
        
        Returns:
            Dictionary with demotion details
        """
        token = db.get_token(token_id)
        if not token:
            raise ValueError(f"Token not found: {token_id}")
        
        if token.status != 'CONFIRMED':
            raise ValueError(f"Can only demote confirmed tokens. Current status: {token.status}")
        
        slot = db.get_time_slot(token.slot_id)
        if not slot:
            raise ValueError(f"Slot not found: {token.slot_id}")
        
        # Remove from confirmed list
        slot.remove_token(token_id)
        
        # Add to waitlist
        slot.add_to_waitlist(token_id)
        position = self.queue_manager.add_to_waitlist(slot.id, token_id, token.priority)
        
        # Update token status
        token.update_status('WAITLISTED', f'Demoted to accommodate higher priority token')
        token.token_number = None  # Clear token number
        token.estimated_time = None  # Clear estimated time
        
        return {
            'demoted_token_id': token_id,
            'new_waitlist_position': position,
            'message': f'Token demoted to waitlist at position {position}'
        }
    
    def _promote_from_waitlist(self, slot_id: str) -> Optional[str]:
        """
        Promote the highest priority token from waitlist to confirmed
        
        Returns:
            Promoted token ID, or None if waitlist is empty
        """
        # Get next token from waitlist
        next_token_id = self.queue_manager.get_next_from_waitlist(slot_id)
        if not next_token_id:
            return None
        
        token = db.get_token(next_token_id)
        slot = db.get_time_slot(slot_id)
        
        if not token or not slot:
            return None
        
        # Remove from waitlist
        slot.remove_from_waitlist(token.id)
        self.queue_manager.remove_from_waitlist(slot_id, token.id)
        
        # Add to confirmed
        slot.add_token(token.id)
        
        # Update token
        token.token_number = slot.allocated_count
        token.calculate_estimated_time(slot.start_time, token.token_number)
        token.update_status('CONFIRMED', 'Promoted from waitlist')
        
        return token.id
    
    def complete_token(self, token_id: str) -> dict:
        """
        Mark a token as completed (consultation done)
        
        Returns:
            Dictionary with completion details
        """
        token = db.get_token(token_id)
        if not token:
            raise ValueError(f"Token not found: {token_id}")
        
        if token.status != 'CONFIRMED':
            raise ValueError(f"Only confirmed tokens can be completed. Current status: {token.status}")
        
        token.update_status('COMPLETED', 'Consultation completed')
        
        return {
            'completed_token_id': token_id,
            'message': 'Token marked as completed'
        }
    
    def get_token_details(self, token_id: str) -> dict:
        """Get detailed information about a token"""
        token = db.get_token(token_id)
        if not token:
            raise ValueError(f"Token not found: {token_id}")
        
        patient = db.get_patient(token.patient_id)
        doctor = db.get_doctor(token.doctor_id)
        slot = db.get_time_slot(token.slot_id)
        
        details = token.to_dict_detailed()
        details['patient'] = patient.to_dict() if patient else None
        details['doctor_name'] = doctor.name if doctor else 'Unknown'
        details['slot_time'] = f"{slot.start_time} - {slot.end_time}" if slot else 'Unknown'
        details['slot_date'] = slot.date if slot else 'Unknown'
        
        if token.status == 'WAITLISTED':
            details['waitlist_position'] = self.queue_manager.get_waitlist_position(token.slot_id, token.id)
        
        return details
