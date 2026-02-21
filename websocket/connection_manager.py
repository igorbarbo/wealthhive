"""
Connection management for WebSocket
"""

from typing import Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """
    Manage WebSocket connections with rooms and authentication
    """
    
    def __init__(self):
        # user_id -> websocket
        self.user_connections: Dict[str, WebSocket] = {}
        
        # room_name -> set of websockets
        self.rooms: Dict[str, Set[WebSocket]] = {}
        
        # websocket -> user_id
        self.websocket_users: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Register new connection"""
        await websocket.accept()
        
        if user_id:
            self.user_connections[user_id] = websocket
            self.websocket_users[websocket] = user_id
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        user_id = self.websocket_users.pop(websocket, None)
        if user_id:
            self.user_connections.pop(user_id, None)
        
        # Remove from all rooms
        for room in self.rooms.values():
            room.discard(websocket)
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Add connection to room"""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove connection from room"""
        if room in self.rooms:
            self.rooms[room].discard(websocket)
    
    async def broadcast_to_room(self, room: str, message: dict):
        """Send message to all in room"""
        if room not in self.rooms:
            return
        
        disconnected = []
        
        for websocket in self.rooms[room]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        # Cleanup
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except Exception:
                self.disconnect(self.user_connections[user_id])
