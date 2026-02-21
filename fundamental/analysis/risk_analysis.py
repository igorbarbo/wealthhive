"""
Fundamental risk analysis
"""

from typing import Any, Dict


class FundamentalRisk:
    """
    Analyze fundamental risks
    """
    
    def business_risk(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess business risk
        
        Factors: industry cyclicality, competitive position, diversification
        """
        risks = []
        score = 100
        
        # Revenue concentration
        if company.get("customer_concentration", 0) > 0.3:
            risks.append("High customer concentration")
            score -= 15
        
        # Geographic concentration
        if company.get("geographic_diversification", 1) < 3:
            risks.append("Limited geographic diversification")
            score -= 10
        
        # Industry cyclicality
        cyclical_sectors = ["Materials", "Energy", "Industrials", "Financials"]
        if company.get("sector") in cyclical_sectors:
            risks.append("Cyclical industry exposure")
            score -= 10
        
        # Competitive position
        market_share = company.get("market_share", 0)
        if market_share < 0.05:
            risks.append("Low market share")
            score -= 10
        
        return {
            "score": max(0, score),
            "risks": risks,
            "level": "High" if score < 50 else "Medium" if score < 75 else "Low",
        }
    
    def financial_risk(self, financials: Dict[str, float]) -> Dict[str, Any]:
        """
        Assess financial risk
        """
        risks = []
        score = 100
        
        # Leverage
        de_ratio = financials.get("debt_to_equity", 50)
        if de_ratio > 100:
            risks.append("High leverage")
            score -= 20
        elif de_ratio > 50:
            risks.append("Moderate leverage")
            score -= 10
        
        # Liquidity
        current_ratio = financials.get("current_ratio", 1.5)
        if current_ratio < 1:
            risks.append("Liquidity concerns")
            score -= 20
        elif current_ratio < 1.5:
            risks.append("Below optimal liquidity")
            score -= 5
        
        # Interest coverage
        ic_ratio = financials.get("interest_coverage", 5)
        if ic_ratio < 2:
            risks.append("Poor interest coverage")
            score -= 25
        elif ic_ratio < 5:
            risks.append("Adequate interest coverage")
            score -= 5
        
        return {
            "score": max(0, score),
            "risks": risks,
            "level": "High" if score < 50 else "Medium" if score < 75 else "Low",
        }
    
    def earnings_quality(self, financials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess earnings quality
        
        High quality = cash earnings close to reported earnings
        """
        net_income = financials.get("net_income", 0)
        operating_cash_flow = financials.get("operating_cash_flow", 0)
        
        if net_income == 0:
            return {"score": 0, "quality": "Unknown"}
        
        # Accruals ratio
        accruals = (net_income - operating_cash_flow) / net_income
        
        # Score based on accruals
        if abs(accruals) < 0.1:
            quality = "High"
            score = 90
        elif abs(accruals) < 0.2:
            quality = "Good"
            score = 75
        elif abs(accruals) < 0.4:
            quality = "Fair"
            score = 50
        else:
            quality = "Poor"
            score = 25
        
        return {
            "score": score,
            "quality": quality,
            "accruals_ratio": round(accruals, 3),
            "interpretation": "Low accruals indicate high earnings quality",
        }
    
    def comprehensive_risk_assessment(
        self,
        company: Dict[str, Any],
        financials: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Comprehensive risk assessment
        """
        business = self.business_risk(company)
        financial = self.financial_risk(financials)
        earnings = self.earnings_quality(financials)
        
        # Overall risk score (weighted average)
        overall = (
            business["score"] * 0.3 +
            financial["score"] * 0.4 +
            earnings["score"] * 0.3
        )
        
        all_risks = business["risks"] + financial["risks"]
        
        return {
            "overall_score": round(overall, 1),
            "risk_level": "High" if overall < 50 else "Medium" if overall < 75 else "Low",
            "breakdown": {
                "business_risk": business,
                "financial_risk": financial,
                "earnings_quality": earnings,
            },
            "key_risks": all_risks[:5],  # Top 5 risks
            "recommendation": self._risk_recommendation(overall, all_risks),
        }
    
    def _risk_recommendation(self, score: float, risks: list) -> str:
        """Generate risk-based recommendation"""
        if score >= 80:
            return "Low risk profile suitable for conservative investors"
        elif score >= 60:
            return "Moderate risk - monitor key risk factors"
        elif score >= 40:
            return "Elevated risk - requires careful monitoring"
        else:
            return "High risk - suitable only for risk-tolerant investors"
          
