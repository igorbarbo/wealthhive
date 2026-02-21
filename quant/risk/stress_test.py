"""
Stress testing scenarios
"""

from typing import Dict, List

import numpy as np


class StressTest:
    """
    Portfolio stress testing
    """
    
    SCENARIOS = {
        "2008_crisis": {
            "stocks": -0.40,
            "bonds": 0.05,
            "reits": -0.35,
            "commodities": -0.20,
        },
        "covid_crash": {
            "stocks": -0.35,
            "bonds": 0.02,
            "reits": -0.30,
            "commodities": -0.25,
        },
        "interest_rate_shock": {
            "stocks": -0.15,
            "bonds": -0.10,
            "reits": -0.20,
            "commodities": 0.05,
        },
        "inflation_spike": {
            "stocks": -0.10,
            "bonds": -0.15,
            "reits": 0.05,
            "commodities": 0.20,
        },
    }
    
    def run_test(
        self,
        portfolio,
        scenario_name: str,
    ) -> Dict:
        """
        Run stress test scenario
        
        Args:
            portfolio: Portfolio to test
            scenario_name: Name of predefined scenario
        """
        if scenario_name not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario = self.SCENARIOS[scenario_name]
        
        # Map portfolio to asset classes
        allocation = self._map_to_asset_classes(portfolio)
        
        # Calculate impact
        total_impact = 0
        impacts = {}
        
        for asset_class, weight in allocation.items():
            shock = scenario.get(asset_class, 0)
            impact = weight * shock
            impacts[asset_class] = {
                "weight": weight,
                "shock": shock,
                "impact": impact,
            }
            total_impact += impact
        
        portfolio_value = portfolio.total_value or 0
        
        return {
            "scenario": scenario_name,
            "portfolio_value_before": portfolio_value,
            "portfolio_value_after": portfolio_value * (1 + total_impact),
            "total_impact": total_impact,
            "impact_percent": total_impact * 100,
            "breakdown": impacts,
        }
    
    def run_all_tests(self, portfolio) -> List[Dict]:
        """Run all stress test scenarios"""
        results = []
        for scenario in self.SCENARIOS.keys():
            result = self.run_test(portfolio, scenario)
            results.append(result)
        return results
    
    def _map_to_asset_classes(self, portfolio) -> Dict[str, float]:
        """Map portfolio positions to asset classes"""
        # Simplified mapping
        # Would use actual asset classification
        return {
            "stocks": 0.60,
            "bonds": 0.30,
            "reits": 0.10,
        }
    
    def custom_scenario(
        self,
        portfolio,
        shocks: Dict[str, float],
    ) -> Dict:
        """Run custom stress test"""
        # Temporarily add scenario
        scenario_name = "custom"
        self.SCENARIOS[scenario_name] = shocks
        
        result = self.run_test(portfolio, scenario_name)
        
        # Remove temporary scenario
        del self.SCENARIOS[scenario_name]
        
        return result
