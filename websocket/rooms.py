"""
Room management for WebSocket
"""

from typing import Dict, Set


class RoomManager:
    """
    Manage chat rooms / channels
    """
    
    def __init__(self):
        self.rooms: Dict[str, Set] = {}  # room_id -> set of connections
        self.user_rooms: Dict[str, Set] = {}  # user_id -> set of room_ids
    
    def create_room(self, room_id: str):
        """Create new room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
    
    def delete_room(self, room_id: str):
        """Delete room"""
        self.rooms.pop(room_id, None)
    
    def join(self, room_id: str, connection):
        """Add connection to room"""
        if room_id not in self.rooms:
            self.create_room(room_id)
        self.rooms[room_id].add(connection)
    
    def leave(self, room_id: str, connection):
        """Remove connection from room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(connection)
            if not self.rooms[room_id]:
                self.delete_room(room_id)
    
    def get_room_members(self, room_id: str) -> int:
        """Get number of members in room"""
        return len(self.rooms.get(room_id, set()))
    
    def get_user_rooms(self, user_id: str) -> Set[str]:
        """Get rooms user is in"""
        return self.user_rooms.get(user_id, set())
