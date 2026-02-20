"""
Alpha Vantage data provider
"""

from typing import Any, Dict, List

import httpx

from app.config import settings


class AlphaVantageProvider:
    """Alpha Vantage API client"""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get global quote"""
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key,
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        data = response.json()
        
        quote = data.get("Global Quote", {})
        
        return {
            "symbol": quote.get("01. symbol"),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "0%"),
            "volume": int(quote.get("06. volume", 0)),
        }
    
    async def get_time_series(
        self,
        symbol: str,
        interval: str = "daily",
    ) -> List[Dict[str, Any]]:
        """Get time series data"""
        function = f"TIME_SERIES_{interval.upper()}"
        
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        data = response.json()
        
        time_series_key = f"Time Series ({interval})"
        time_series = data.get(time_series_key, {})
        
        result = []
        for date, values in time_series.items():
            result.append({
                "date": date,
                "open": float(values.get("1. open", 0)),
                "high": float(values.get("2. high", 0)),
                "low": float(values.get("3. low", 0)),
                "close": float(values.get("4. close", 0)),
                "volume": int(values.get("5. volume", 0)),
            })
        
        return result
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data"""
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key,
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        data = response.json()
        
        return {
            "symbol": data.get("Symbol"),
            "name": data.get("Name"),
            "description": data.get("Description"),
            "sector": data.get("Sector"),
            "industry": data.get("Industry"),
            "market_cap": int(data.get("MarketCapitalization", 0)),
            "pe_ratio": float(data.get("PERatio", 0)),
            "pb_ratio": float(data.get("PriceToBookRatio", 0)),
            "dividend_yield": float(data.get("DividendYield", 0)),
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
