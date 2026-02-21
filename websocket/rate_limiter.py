"""
Rate limiting for WebSocket connections
"""

import time
from typing import Dict


class WebSocketRateLimiter:
    """
    Rate limit WebSocket messages
    """
    
    def __init__(self, max_messages: int = 100, window_seconds: int = 60):
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.clients: Dict[str, list] = {}  # client_id -> list of timestamps
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client can send message"""
        now = time.time()
        
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        # Remove old timestamps
        self.clients[client_id] = [
            ts for ts in self.clients[client_id]
            if now - ts < self.window_seconds
        ]
        
        # Check limit
        if len(self.clients[client_id]) >= self.max_messages:
            return False
        
        # Record message
        self.clients[client_id].append(now)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining messages in window"""
        if client_id not in self.clients:
            return self.max_messages
        
        now = time.time()
        recent = len([ts for ts in self.clients[client_id] if now - ts < self.window_seconds])
        
        return max(0, self.max_messages - recent)
      
