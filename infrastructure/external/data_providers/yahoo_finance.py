"""
Yahoo Finance data provider
"""

from typing import Any, Dict, List, Optional

import yfinance as yf


class YahooFinanceProvider:
    """Yahoo Finance data provider"""
    
    async def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get latest price
            hist = ticker.history(period="1d")
            if not hist.empty:
                latest = hist.iloc[-1]
                current_price = latest["Close"]
                prev_close = info.get("previousClose", current_price)
                change = current_price - prev_close
                change_percent = (change / prev_close) * 100 if prev_close else 0
            else:
                current_price = info.get("currentPrice", 0)
                change = 0
                change_percent = 0
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "volume": info.get("volume", 0),
                "timestamp": info.get("regularMarketTime"),
                "currency": info.get("currency", "BRL"),
            }
        except Exception as e:
            raise Exception(f"Yahoo Finance error: {str(e)}")
    
    async def get_current_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get prices for multiple symbols"""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = await self.get_current_price(symbol)
            except Exception:
                results[symbol] = {"error": "Failed to fetch"}
        return results
    
    async def get_history(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "date": date.isoformat(),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"]),
                })
            
            return data
        except Exception as e:
            raise Exception(f"Yahoo Finance error: {str(e)}")
    
    async def get_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "eps": info.get("trailingEps"),
                "revenue": info.get("totalRevenue"),
                "debt_to_equity": info.get("debtToEquity"),
                "return_on_equity": info.get("returnOnEquity"),
            }
        except Exception as e:
            raise Exception(f"Yahoo Finance error: {str(e)}")
          
