"""
Models package initialization
"""
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.time_slot import TimeSlot
from app.models.token import Token

__all__ = ['Patient', 'Doctor', 'TimeSlot', 'Token']
