"""
B3 WebSocket client for real-time market data
"""

import asyncio
import json

import websockets


class B3WebSocketClient:
    """
    Client for B3 real-time market data WebSocket
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.ws = None
        self.subscriptions = set()
        self.callbacks = []
    
    async def connect(self):
        """Connect to B3 WebSocket"""
        uri = f"wss://api.b3.com.br/market-data?token={self.api_key}"
        self.ws = await websockets.connect(uri)
        
        # Start listener
        asyncio.create_task(self._listen())
    
    async def _listen(self):
        """Listen for messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("B3 connection closed")
            await self.reconnect()
    
    async def _handle_message(self, data: dict):
        """Handle incoming message"""
        for callback in self.callbacks:
            await callback(data)
    
    async def subscribe(self, symbols: list):
        """Subscribe to symbols"""
        if self.ws:
            await self.ws.send(json.dumps({
                "action": "subscribe",
                "symbols": symbols,
            }))
            self.subscriptions.update(symbols)
    
    async def unsubscribe(self, symbols: list):
        """Unsubscribe from symbols"""
        if self.ws:
            await self.ws.send(json.dumps({
                "action": "unsubscribe",
                "symbols": symbols,
            }))
            self.subscriptions.difference_update(symbols)
    
    async def reconnect(self):
        """Reconnect and resubscribe"""
        await asyncio.sleep(5)
        await self.connect()
        await self.subscribe(list(self.subscriptions))
    
    def add_callback(self, callback):
        """Add message callback"""
        self.callbacks.append(callback)
    
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
          
