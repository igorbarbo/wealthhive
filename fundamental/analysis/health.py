"""
Financial health analysis
"""

from typing import Any, Dict


class FinancialHealth:
    """
    Analyze
        Analyze financial health of company
    """
    
    def analyze(self, financials: Dict[str, float]) -> Dict[str, Any]:
        """
        Comprehensive financial health analysis
        
        Returns health scores (0-100) for different categories
        """
        scores = {
            "liquidity": self._liquidity_score(financials),
            "solvency": self._solvency_score(financials),
            "profitability": self._profitability_score(financials),
            "efficiency": self._efficiency_score(financials),
        }
        
        # Overall health score
        scores["overall"] = sum(scores.values()) / len(scores)
        
        # Health rating
        if scores["overall"] >= 80:
            rating = "Excellent"
        elif scores["overall"] >= 60:
            rating = "Good"
        elif scores["overall"] >= 40:
            rating = "Fair"
        else:
            rating = "Poor"
        
        scores["rating"] = rating
        
        return scores
    
    def _liquidity_score(self, f: Dict[str, float]) -> float:
        """Calculate liquidity health score"""
        current_ratio = f.get("current_ratio", 1)
        quick_ratio = f.get("quick_ratio", 0.8)
        
        # Current ratio: 2.0 is ideal
        current_score = min(100, (current_ratio / 2.0) * 100)
        
        # Quick ratio: 1.0 is ideal
        quick_score = min(100, (quick_ratio / 1.0) * 100)
        
        return (current_score + quick_score) / 2
    
    def _solvency_score(self, f: Dict[str, float]) -> float:
        """Calculate solvency health score"""
        debt_to_equity = f.get("debt_to_equity", 100)
        interest_coverage = f.get("interest_coverage", 3)
        
        # Debt/Equity: lower is better, 50% is good
        de_score = max(0, min(100, (100 - debt_to_equity)))
        
        # Interest coverage: higher is better, 5x is good
        ic_score = min(100, (interest_coverage / 5.0) * 100)
        
        return (de_score + ic_score) / 2
    
    def _profitability_score(self, f: Dict[str, float]) -> float:
        """Calculate profitability score"""
        roe = f.get("roe", 0.1)
        roa = f.get("roa", 0.05)
        margin = f.get("net_margin", 0.1)
        
        # ROE: 15% is good
        roe_score = min(100, (roe / 0.15) * 100)
        
        # ROA: 8% is good
        roa_score = min(100, (roa / 0.08) * 100)
        
        # Margin: 15% is good
        margin_score = min(100, (margin / 0.15) * 100)
        
        return (roe_score + roa_score + margin_score) / 3
    
    def _efficiency_score(self, f: Dict[str, float]) -> float:
        """Calculate efficiency score"""
        asset_turnover = f.get("asset_turnover", 0.5)
        inventory_turnover = f.get("inventory_turnover", 6)
        
        # Asset turnover: 1.0 is good
        at_score = min(100, (asset_turnover / 1.0) * 100)
        
        # Inventory turnover: 12 is good
        it_score = min(100, (inventory_turnover / 12.0) * 100)
        
        return (at_score + it_score) / 2
    
    def altman_z_score(
        self,
        working_capital: float,
        retained_earnings: float,
        ebit: float,
        market_cap: float,
        sales: float,
        total_assets: float,
        total_liabilities: float,
    ) -> Dict[str, Any]:
        """
        Calculate Altman Z-Score for bankruptcy prediction
        
        Z > 2.99: Safe zone
        1.81 < Z < 2.99: Grey zone
        Z < 1.81: Distress zone
        """
        A = working_capital / total_assets
        B = retained_earnings / total_assets
        C = ebit / total_assets
        D = market_cap / total_liabilities
        E = sales / total_assets
        
        Z = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
        
        if Z > 2.99:
            zone = "Safe"
            risk = "Low"
        elif Z > 1.81:
            zone = "Grey"
            risk = "Medium"
        else:
            zone = "Distress"
            risk = "High"
        
        return {
            "z_score": round(Z, 2),
            "zone": zone,
            "bankruptcy_risk": risk,
            "components": {
                "A": round(A, 3),
                "B": round(B, 3),
                "C": round(C, 3),
                "D": round(D, 3),
                "E": round(E, 3),
            },
        }
        
