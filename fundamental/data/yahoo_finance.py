"""
Yahoo Finance fundamental data
"""

from typing import Any, Dict

import yfinance as yf


class YahooFundamentals:
    """
    Fetch fundamental data from Yahoo Finance
    """
    
    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive fundamental data"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                
                # Valuation
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "pb_ratio": info.get("priceToBook"),
                "ps_ratio": info.get("priceToSalesTrailing12Months"),
                
                # Profitability
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "roa": info.get("returnOnAssets"),
                "roe": info.get("returnOnEquity"),
                
                # Financial health
                "current_ratio": info.get("currentRatio"),
                "debt_to_equity": info.get("debtToEquity"),
                "quick_ratio": info.get("quickRatio"),
                
                # Growth
                "revenue_growth": info.get("revenueGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                
                # Dividends
                "dividend_rate": info.get("dividendRate"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                
                # Price targets
                "target_high": info.get("targetHighPrice"),
                "target_low": info.get("targetLowPrice"),
                "target_mean": info.get("targetMeanPrice"),
                "recommendation": info.get("recommendationKey"),
            }
        
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    async def get_financials(self, ticker: str) -> Dict[str, Any]:
        """Get financial statements"""
        try:
            stock = yf.Ticker(ticker)
            
            return {
                "income_statement": stock.income_stmt.to_dict() if stock.income_stmt is not None else {},
                "balance_sheet": stock.balance_sheet.to_dict() if stock.balance_sheet is not None else {},
                "cash_flow": stock.cashflow.to_dict() if stock.cashflow is not None else {},
            }
        
        except Exception as e:
            return {"error": str(e)}
          
