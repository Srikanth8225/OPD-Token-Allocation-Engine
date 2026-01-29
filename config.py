"""
Configuration settings for OPD Token Allocation Engine
"""
from datetime import datetime

class Config:
    """Application configuration"""
    
    # Application settings
    DEBUG = True
    TESTING = False
    
    # Token allocation settings
    DEFAULT_SLOT_DURATION_MINUTES = 60
    DEFAULT_SLOT_CAPACITY = 10
    
    # Priority levels (lower number = higher priority)
    PRIORITY_LEVELS = {
        'EMERGENCY': 1,
        'PAID_PRIORITY': 2,
        'FOLLOW_UP': 3,
        'ONLINE_BOOKING': 4,
        'WALK_IN': 5
    }
    
    # Token source types
    TOKEN_SOURCES = ['EMERGENCY', 'PAID_PRIORITY', 'FOLLOW_UP', 'ONLINE_BOOKING', 'WALK_IN']
    
    # Token status types
    TOKEN_STATUS = ['CONFIRMED', 'WAITLISTED', 'CANCELLED', 'NO_SHOW', 'COMPLETED']
    
    # Time settings
    NO_SHOW_GRACE_PERIOD_MINUTES = 15
    AVERAGE_CONSULTATION_MINUTES = 5
    
    # Slot settings
    ALLOW_WAITLIST = True
    MAX_WAITLIST_SIZE = 20
