"""
Priority Manager - Handles priority-based token ordering
"""
from typing import List, Tuple
from datetime import datetime
from config import Config

class PriorityManager:
    """Manages priority levels and ordering for tokens"""
    
    @staticmethod
    def get_priority_for_source(source: str) -> int:
        """Get priority level for a token source"""
        return Config.PRIORITY_LEVELS.get(source, 999)
    
    @staticmethod
    def sort_by_priority(tokens: List[Tuple[str, int, datetime]]) -> List[Tuple[str, int, datetime]]:
        """
        Sort tokens by priority and timestamp
        
        Args:
            tokens: List of tuples (token_id, priority, timestamp)
            
        Returns:
            Sorted list with highest priority first
        """
        return sorted(tokens, key=lambda x: (x[1], x[2]))
    
    @staticmethod
    def compare_priority(priority1: int, priority2: int) -> int:
        """
        Compare two priority levels
        
        Returns:
            -1 if priority1 is higher (lower number)
            0 if equal
            1 if priority2 is higher
        """
        if priority1 < priority2:
            return -1
        elif priority1 > priority2:
            return 1
        return 0
    
    @staticmethod
    def should_demote(existing_priority: int, new_priority: int) -> bool:
        """
        Check if an existing token should be demoted for a new token
        
        Args:
            existing_priority: Priority of existing token
            new_priority: Priority of new token (e.g., emergency)
            
        Returns:
            True if new token has higher priority
        """
        return new_priority < existing_priority
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """Validate if source type is allowed"""
        return source in Config.TOKEN_SOURCES
