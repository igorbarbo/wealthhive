"""
Complete investment research report
"""

from typing import Any, Dict

from fundamental.analysis.health import FinancialHealth
from fundamental.analysis.multiples import MultiplesAnalysis
from fundamental.analysis.valuation import ValuationModels


class InvestmentReport:
    """
    Generate comprehensive investment research report
    """
    
    def __init__(self):
        self.valuation = ValuationModels()
        self.multiples = MultiplesAnalysis()
        self.health = FinancialHealth()
    
    async def generate(
        self,
        ticker: str,
        company_data: Dict[str, Any],
        financials: Dict[str, float],
        peers: list,
    ) -> Dict[str, Any]:
        """
        Generate complete investment report
        """
        # Executive summary
        summary = self._executive_summary(company_data, financials)
        
        # Business overview
        business = self._business_overview(company_data)
        
        # Financial analysis
        financial_analysis = self._financial_analysis(financials)
        
        # Valuation
        valuation = self._valuation_analysis(ticker, financials, peers)
        
        # Investment thesis
        thesis = self._investment_thesis(summary, valuation)
        
        # Risks
        risks = self._risk_assessment(company_data, financials)
        
        return {
            "ticker": ticker,
            "date_generated": "",  # Current date
            "executive_summary": summary,
            "business_overview": business,
            "financial_analysis": financial_analysis,
            "valuation": valuation,
            "investment_thesis": thesis,
            "risks": risks,
            "recommendation": self._final_recommendation(valuation, risks),
        }
    
    def _executive_summary(self, company: Dict, financials: Dict) -> Dict:
        """Generate executive summary"""
        return {
            "company_name": company.get("name"),
            "sector": company.get("sector"),
            "market_cap": company.get("market_cap"),
            "investment_highlights": self._extract_highlights(company, financials),
            "key_metrics": {
                "pe_ratio": financials.get("pe_ratio"),
                "pb_ratio": financials.get("pb_ratio"),
                "dividend_yield": financials.get("dividend_yield"),
                "roe": financials.get("roe"),
            },
        }
    
    def _business_overview(self, company: Dict) -> Dict:
        """Business overview"""
        return {
            "description": company.get("description"),
            "business_model": company.get("business_model"),
            "competitive_advantages": company.get("moat", []),
            "industry_position": company.get("market_position"),
        }
    
    def _financial_analysis(self, financials: Dict) -> Dict:
        """Financial health analysis"""
        health_score = self.health.analyze(financials)
        
        return {
            "health_score": health_score,
            "profitability_trend": "improving",  # Would calculate
            "balance_sheet_strength": "strong" if health_score["solvency"] > 70 else "moderate",
            "cash_flow_quality": "high" if health_score["overall"] > 70 else "moderate",
        }
    
    def _valuation_analysis(
        self,
        ticker: str,
        financials: Dict,
        peers: list,
    ) -> Dict:
        """Valuation analysis"""
        # DCF valuation
        dcf = self.valuation.dcf(
            free_cash_flow=financials.get("free_cash_flow", 0),
            growth_rate=0.05,
            discount_rate=0.10,
            terminal_growth=0.03,
        )
        
        # Multiples comparison
        multiples = self.multiples.compare_multiples(financials, peers)
        
        # Fair value estimate
        fair_value = self._estimate_fair_value(dcf, multiples)
        
        current_price = financials.get("current_price", 0)
        upside = (fair_value - current_price) / current_price if current_price > 0 else 0
        
        return {
            "dcf_valuation": dcf["enterprise_value"],
            "multiples_analysis": multiples,
            "fair_value_estimate": fair_value,
            "current_price": current_price,
            "upside_potential": upside,
            "valuation_rating": "undervalued" if upside > 0.2 else "fair" if upside > -0.1 else "overvalued",
        }
    
    def _estimate_fair_value(self, dcf: Dict, multiples: Dict) -> float:
        """Estimate fair value from multiple methods"""
        dcf_value = dcf.get("enterprise_value", 0)
        
        # Average of methods
        values = [v for v in [dcf_value] if v > 0]
        
        return sum(values) / len(values) if values else 0
    
    def _investment_thesis(self, summary: Dict, valuation: Dict) -> Dict:
        """Investment thesis"""
        upside = valuation.get("upside_potential", 0)
        
        if upside > 0.3:
            thesis = "Strong buy - significant undervaluation"
            bull_case = "Multiple expansion and earnings growth"
            bear_case = "Execution risk and market downturn"
        elif upside > 0.1:
            thesis = "Buy - moderate undervaluation"
            bull_case = "Steady growth and margin improvement"
            bear_case = "Competitive pressure"
        else:
            thesis = "Hold - fairly valued"
            bull_case = "Defensive characteristics"
            bear_case = "Limited upside"
        
        return {
            "thesis": thesis,
            "bull_case": bull_case,
            "bear_case": bear_case,
            "catalysts": self._identify_catalysts(summary),
        }
    
    def _identify_catalysts(self, summary: Dict) -> list:
        """Identify potential catalysts"""
        return [
            "Earnings releases",
            "Product launches",
            "Strategic initiatives",
            "Industry trends",
        ]
    
    def _risk_assessment(self, company: Dict, financials: Dict) -> Dict:
        """Risk assessment"""
        from fundamental.analysis.risk_analysis import FundamentalRisk
        
        risk_analyzer = FundamentalRisk()
        return risk_analyzer.comprehensive_risk_assessment(company, financials)
    
    def _final_recommendation(self, valuation: Dict, risks: Dict) -> Dict:
        """Final investment recommendation"""
        upside = valuation.get("upside_potential", 0)
        risk_score = risks.get("overall_score", 50)
        
        # Risk-adjusted recommendation
        if upside > 0.25 and risk_score > 60:
            rating = "BUY"
            conviction = "High"
        elif upside > 0.15 and risk_score > 50:
            rating = "BUY"
            conviction = "Medium"
        elif upside > 0.05:
            rating = "HOLD"
            conviction = "Medium"
        else:
            rating = "SELL"
            conviction = "High"
        
        return {
            "rating": rating,
            "conviction": conviction,
            "target_price": valuation.get("fair_value_estimate"),
            "time_horizon": "12-18 months",
        }
    
    def _extract_highlights(self, company: Dict, financials: Dict) -> list:
        """Extract investment highlights"""
        highlights = []
        
        if financials.get("roe", 0) > 0.15:
            highlights.append("Strong ROE above 15%")
        
        if financials.get("debt_to_equity", 100) < 50:
            highlights.append("Conservative balance sheet")
        
        if company.get("market_share", 0) > 0.2:
            highlights.append("Market leader")
        
        return highlights
      
