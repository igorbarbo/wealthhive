"""
Market data service - orchestrates data from multiple providers
"""

from typing import Any, Dict, List, Optional

import structlog

from infrastructure.cache.redis_client import RedisCache
from infrastructure.external.data_providers.yahoo_finance import YahooFinanceProvider

logger = structlog.get_logger()


class MarketDataService:
    """Service for fetching and caching market data"""
    
    def __init__(self):
        self.cache = RedisCache()
        self.yahoo = YahooFinanceProvider()
        self.cache_ttl = 300  # 5 minutes
    
    async def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price with caching"""
        cache_key = f"price:{symbol}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Fetch from provider
        try:
            data = await self.yahoo.get_current_price(symbol)
            await self.cache.set(cache_key, data, ttl=self.cache_ttl)
            return data
        except Exception as e:
            logger.error("Failed to fetch price", symbol=symbol, error=str(e))
            raise
    
    async def get_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """Get prices for multiple symbols"""
        results = {}
        missing = []
        
        # Check cache for all symbols
        for symbol in symbols:
            cache_key = f"price:{symbol}"
            cached = await self.cache.get(cache_key)
            if cached:
                results[symbol] = cached
            else:
                missing.append(symbol)
        
        # Fetch missing from provider
        if missing:
            try:
                data = await self.yahoo.get_current_prices(missing)
                for symbol, price_data in data.items():
                    results[symbol] = price_data
                    await self.cache.set(f"price:{symbol}", price_data, ttl=self.cache_ttl)
            except Exception as e:
                logger.error("Failed to fetch prices", symbols=missing, error=str(e))
        
        return results
    
    async def get_historical(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Get historical price data"""
        cache_key = f"history:{symbol}:{period}:{interval}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        data = await self.yahoo.get_history(symbol, period, interval)
        await self.cache.set(cache_key, data, ttl=3600)  # 1 hour cache for historical
        
        return data
    
    async def subscribe_realtime(self, symbols: List[str], callback):
        """Subscribe to real-time updates"""
        # Would connect to WebSocket feed
        pass
