"""
Clear (XP) API client - similar to XP but with Clear-specific endpoints
"""

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class ClearClient:
    """Clear Corretora API client"""
    
    BASE_URL = "https://api.clear.com.br/v1"
    
    def __init__(self):
        self.api_key = settings.CLEAR_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        response = await self.client.get("/account")
        response.raise_for_status()
        return response.json()
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        response = await self.client.get("/positions")
        response.raise_for_status()
        return response.json()
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place trading order"""
        payload = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "type": order_type,
        }
        if price:
            payload["price"] = price
        
        response = await self.client.post("/orders", json=payload)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
