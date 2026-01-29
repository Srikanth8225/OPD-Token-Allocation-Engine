"""
Queue Manager - Manages waitlists and token queues
"""
from typing import List, Optional, Dict
from datetime import datetime

class QueueManager:
    """Manages token queues and waitlists"""
    
    def __init__(self):
        self.waitlists: Dict[str, List[Dict]] = {}  # slot_id -> list of waitlist entries
    
    def add_to_waitlist(self, slot_id: str, token_id: str, priority: int) -> int:
        """
        Add a token to slot's waitlist
        
        Returns:
            Position in waitlist (1-indexed)
        """
        if slot_id not in self.waitlists:
            self.waitlists[slot_id] = []
        
        entry = {
            'token_id': token_id,
            'priority': priority,
            'timestamp': datetime.now()
        }
        
        self.waitlists[slot_id].append(entry)
        self._sort_waitlist(slot_id)
        
        # Find position
        for idx, item in enumerate(self.waitlists[slot_id]):
            if item['token_id'] == token_id:
                return idx + 1
        
        return len(self.waitlists[slot_id])
    
    def remove_from_waitlist(self, slot_id: str, token_id: str) -> bool:
        """Remove a token from waitlist"""
        if slot_id not in self.waitlists:
            return False
        
        self.waitlists[slot_id] = [
            item for item in self.waitlists[slot_id] 
            if item['token_id'] != token_id
        ]
        return True
    
    def get_next_from_waitlist(self, slot_id: str) -> Optional[str]:
        """
        Get the highest priority token from waitlist
        
        Returns:
            token_id of next candidate, or None if waitlist empty
        """
        if slot_id not in self.waitlists or not self.waitlists[slot_id]:
            return None
        
        # Waitlist is already sorted by priority
        next_entry = self.waitlists[slot_id][0]
        return next_entry['token_id']
    
    def get_waitlist_position(self, slot_id: str, token_id: str) -> Optional[int]:
        """Get position of token in waitlist (1-indexed)"""
        if slot_id not in self.waitlists:
            return None
        
        for idx, item in enumerate(self.waitlists[slot_id]):
            if item['token_id'] == token_id:
                return idx + 1
        
        return None
    
    def get_waitlist_size(self, slot_id: str) -> int:
        """Get total number of tokens in waitlist"""
        if slot_id not in self.waitlists:
            return 0
        return len(self.waitlists[slot_id])
    
    def _sort_waitlist(self, slot_id: str):
        """Sort waitlist by priority (ascending) and timestamp"""
        if slot_id in self.waitlists:
            self.waitlists[slot_id].sort(key=lambda x: (x['priority'], x['timestamp']))
    
    def get_waitlist_info(self, slot_id: str) -> List[Dict]:
        """Get all waitlist entries for a slot"""
        if slot_id not in self.waitlists:
            return []
        
        return [
            {
                'token_id': entry['token_id'],
                'priority': entry['priority'],
                'position': idx + 1
            }
            for idx, entry in enumerate(self.waitlists[slot_id])
        ]
