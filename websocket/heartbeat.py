"""
WebSocket heartbeat / keepalive
"""

import asyncio
from typing import Dict

from fastapi import WebSocket


class HeartbeatManager:
    """
    Manage WebSocket heartbeats
    """
    
    def __init__(self, interval: int = 30, timeout: int = 60):
        self.interval = interval
        self.timeout = timeout
        self.last_pong: Dict[WebSocket, float] = {}
        self.running = False
    
    async def start(self):
        """Start heartbeat checker"""
        self.running = True
        
        while self.running:
            now = asyncio.get_event_loop().time()
            
            # Check for timeouts
            timed_out = [
                ws for ws, last in self.last_pong.items()
                if now - last > self.timeout
            ]
            
            for ws in timed_out:
                await self.handle_timeout(ws)
            
            await asyncio.sleep(self.interval)
    
    async def handle_timeout(self, websocket: WebSocket):
        """Handle client timeout"""
        try:
            await websocket.close(code=1001)  # Going away
        except Exception:
            pass
    
    def record_pong(self, websocket: WebSocket):
        """Record pong from client"""
        self.last_pong[websocket] = asyncio.get_event_loop().time()
    
    def remove_client(self, websocket: WebSocket):
        """Remove client tracking"""
        self.last_pong.pop(websocket, None)
    
    async def send_ping(self, websocket: WebSocket):
        """Send ping to client"""
        try:
            await websocket.send_json({"type": "ping"})
        except Exception:
            pass
