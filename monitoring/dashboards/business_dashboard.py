"""
Business metrics dashboard
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class KPIData:
    """KPI data structure"""
    name: str
    value: float
    target: float
    unit: str
    trend: str  # up, down, stable
    change_percent: float


class BusinessDashboard:
    """
    Business KPIs dashboard
    """
    
    def __init__(self):
        self._kpis: Dict[str, KPIData] = {}
        self._historical: Dict[str, List[Dict]] = {}
    
    def update_kpi(self, name: str, value: float, target: float,
                   unit: str = "", trend: str = "stable",
                   change_percent: float = 0) -> None:
        """Update KPI value"""
        self._kpis[name] = KPIData(
            name=name,
            value=value,
            target=target,
            unit=unit,
            trend=trend,
            change_percent=change_percent
        )
        
        # Store historical
        if name not in self._historical:
            self._historical[name] = []
        
        self._historical[name].append({
            "timestamp": datetime.utcnow().isoformat(),
            "value": value
        })
    
    def get_portfolio_kpis(self) -> Dict[str, KPIData]:
        """Get portfolio-related KPIs"""
        return {
            k: v for k, v in self._kpis.items()
            if k.startswith("portfolio_")
        }
    
    def get_trading_kpis(self) -> Dict[str, KPIData]:
        """Get trading-related KPIs"""
        return {
            k: v for k, v in self._kpis.items()
            if k.startswith("trading_")
        }
    
    def get_user_kpis(self) -> Dict[str, KPIData]:
        """Get user-related KPIs"""
        return {
            k: v for k, v in self._kpis.items()
            if k.startswith("user_")
        }
    
    def get_ml_kpis(self) -> Dict[str, KPIData]:
        """Get ML-related KPIs"""
        return {
            k: v for k, v in self._kpis.items()
            if k.startswith("ml_")
        }
    
    def get_all_kpis(self) -> Dict[str, Any]:
        """Get all KPIs"""
        return {
            "kpis": {
                name: {
                    "value": kpi.value,
                    "target": kpi.target,
                    "unit": kpi.unit,
                    "trend": kpi.trend,
                    "change_percent": kpi.change_percent,
                    "achievement": (kpi.value / kpi.target * 100) if kpi.target else 0
                }
                for name, kpi in self._kpis.items()
            },
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def get_trend(self, kpi_name: str, days: int = 7) -> List[Dict]:
        """Get KPI trend"""
        if kpi_name not in self._historical:
            return []
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [
            h for h in self._historical[kpi_name]
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]
    
    def calculate_health_score(self) -> float:
        """Calculate overall business health score"""
        if not self._kpis:
            return 0.0
        
        scores = []
        for kpi in self._kpis.values():
            if kpi.target > 0:
                achievement = min(kpi.value / kpi.target, 1.5)  # Cap at 150%
                scores.append(achievement * 100)
        
        return sum(scores) / len(scores) if scores else 0.0
      
