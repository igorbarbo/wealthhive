"""
WebSocket server for real-time data
"""

from typing import Set

import structlog
from fastapi import WebSocket, WebSocketDisconnect

logger = structlog.get_logger()


class WebSocketServer:
    """
    WebSocket server for real-time market data
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: dict = {}  # websocket -> set of symbols
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.subscriptions[websocket] = set()
        logger.info("Client connected", connections=len(self.active_connections))
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        self.active_connections.discard(websocket)
        self.subscriptions.pop(websocket, None)
        logger.info("Client disconnected", connections=len(self.active_connections))
    
    async def subscribe(self, websocket: WebSocket, symbols: list):
        """Subscribe to symbols"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].update(symbols)
            await websocket.send_json({
                "type": "subscribed",
                "symbols": list(self.subscriptions[websocket]),
            })
    
    async def unsubscribe(self, websocket: WebSocket, symbols: list):
        """Unsubscribe from symbols"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].difference_update(symbols)
    
    async def broadcast(self, message: dict, symbol: str = None):
        """Broadcast message to subscribed clients"""
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                # Check subscription if symbol specified
                if symbol and websocket in self.subscriptions:
                    if symbol not in self.subscriptions[websocket]:
                        continue
                
                await websocket.send_json(message)
            
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)
