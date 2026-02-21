"""
Multi-market stock screener
"""

from typing import Any, Dict, List

import pandas as pd


class MultiMarketScreener:
    """
    Screen stocks across multiple markets
    """
    
    MARKETS = ["US", "BR", "EU", "Asia"]
    
    def __init__(self):
        self.criteria = {}
    
    def add_criterion(self, name: str, condition: Dict):
        """
        Add screening criterion
        
        condition: {
            "field": "pe_ratio",
            "operator": "<",
            "value": 15
        }
        """
        self.criteria[name] = condition
    
    def screen(self, universe: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all criteria to stock universe
        
        Args:
            universe: DataFrame with stock data
        """
        result = universe.copy()
        
        for name, criterion in self.criteria.items():
            field = criterion["field"]
            operator = criterion["operator"]
            value = criterion["value"]
            
            if operator == "<":
                result = result[result[field] < value]
            elif operator == ">":
                result = result[result[field] > value]
            elif operator == "==":
                result = result[result[field] == value]
            elif operator == "between":
                result = result[
                    (result[field] >= value[0]) &
                    (result[field] <= value[1])
                ]
        
        return result
    
    def value_screen(self, universe: pd.DataFrame) -> pd.DataFrame:
        """Pre-configured value screen"""
        self.criteria = {
            "low_pe": {"field": "pe_ratio", "operator": "<", "value": 15},
            "low_pb": {"field": "pb_ratio", "operator": "<", "value": 2},
            "dividend": {"field": "dividend_yield", "operator": ">", "value": 0.03},
        }
        return self.screen(universe)
    
    def growth_screen(self, universe: pd.DataFrame) -> pd.DataFrame:
        """Pre-configured growth screen"""
        self.criteria = {
            "revenue_growth": {"field": "revenue_growth", "operator": ">", "value": 0.15},
            "earnings_growth": {"field": "earnings_growth", "operator": ">", "value": 0.15},
            "roe": {"field": "roe", "operator": ">", "value": 0.15},
        }
        return self.screen(universe)
    
    def quality_screen(self, universe: pd.DataFrame) -> pd.DataFrame:
        """Pre-configured quality screen"""
        self.criteria = {
            "low_debt": {"field": "debt_to_equity", "operator": "<", "value": 0.5},
            "high_roe": {"field": "roe", "operator": ">", "value": 0.15},
            "consistent": {"field": "earnings_variance", "operator": "<", "value": 0.2},
        }
        return self.screen(universe)
    
    def rank_results(
        self,
        results: pd.DataFrame,
        ranking_criteria: List[str],
    ) -> pd.DataFrame:
        """
        Rank screening results
        
        Args:
            results: Filtered DataFrame
            ranking_criteria: List of columns to rank by
        """
        # Calculate composite score
        scores = pd.DataFrame(index=results.index)
        
        for criterion in ranking_criteria:
            if criterion in results.columns:
                # Normalize to 0-100
                min_val = results[criterion].min()
                max_val = results[criterion].max()
                
                if max_val > min_val:
                    scores[criterion] = (
                        (results[criterion] - min_val) / (max_val - min_val) * 100
                    )
                else:
                    scores[criterion] = 50
        
        # Average score
        results["composite_score"] = scores.mean(axis=1)
        
        # Sort by score
        return results.sort_values("composite_score", ascending=False)
    
    def export_results(self, results: pd.DataFrame, format: str = "csv") -> str:
        """Export screening results"""
        if format == "csv":
            return results.to_csv()
        elif format == "json":
            return results.to_json(orient="records")
        elif format == "excel":
            # Would return bytes
            return ""
        else:
            raise ValueError(f"Unknown format: {format}")
      
