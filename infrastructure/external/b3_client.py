"""
B3 (Brazilian Stock Exchange) API client
"""

from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class B3Client:
    """Client for B3 market data"""
    
    BASE_URL = "https://api.b3.com.br/v1"  # Example URL
    
    def __init__(self):
        self.api_key = settings.B3_API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )
    
    async def get_quote(self, ticker: str) -> Dict[str, Any]:
        """Get current quote for ticker"""
        try:
            response = await self.client.get(f"/quotes/{ticker}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"B3 API error: {str(e)}")
    
    async def get_historical(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        """Get historical data"""
        response = await self.client.get(
            f"/quotes/{ticker}/historical",
            params={"start": start_date, "end": end_date},
        )
        response.raise_for_status()
        return response.json()
    
    async def get_intraday(self, ticker: str) -> List[Dict[str, Any]]:
        """Get intraday data"""
        response = await self.client.get(f"/quotes/{ticker}/intraday")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
