"""
Custom business metrics for WealthHive
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import asyncio


@dataclass
class BusinessMetric:
    """Business-level metric"""
    name: str
    value: float
    category: str  # portfolio, trading, user, system
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CustomMetrics:
    """
    Track custom business metrics
    """
    
    def __init__(self):
        self._metrics: Dict[str, list] = defaultdict(list)
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    # Portfolio Metrics
    def record_portfolio_value(self, portfolio_id: str, value: float, currency: str = "BRL") -> None:
        """Record portfolio total value"""
        metric = BusinessMetric(
            name="portfolio_total_value",
            value=value,
            category="portfolio",
            metadata={"portfolio_id": portfolio_id, "currency": currency}
        )
        self._metrics["portfolio_value"].append(metric)
    
    def record_portfolio_return(self, portfolio_id: str, return_pct: float, period: str) -> None:
        """Record portfolio return percentage"""
        metric = BusinessMetric(
            name="portfolio_return",
            value=return_pct,
            category="portfolio",
            metadata={"portfolio_id": portfolio_id, "period": period}
        )
        self._metrics["portfolio_return"].append(metric)
    
    # Trading Metrics
    def record_trade(self, trade_type: str, asset: str, volume: float, value: float) -> None:
        """Record executed trade"""
        self._counters["total_trades"] += 1
        self._counters[f"trades_{trade_type}"] += 1
        
        metric = BusinessMetric(
            name="trade_executed",
            value=value,
            category="trading",
            metadata={"type": trade_type, "asset": asset, "volume": volume}
        )
        self._metrics["trades"].append(metric)
    
    def record_order_latency(self, latency_ms: float) -> None:
        """Record order execution latency"""
        self._histograms["order_latency"].append(latency_ms)
    
    # User Metrics
    def record_user_login(self, user_id: str, success: bool) -> None:
        """Record user login attempt"""
        status = "success" if success else "failure"
        self._counters[f"login_{status}"] += 1
    
    def record_api_call(self, endpoint: str, duration_ms: float, status_code: int) -> None:
        """Record API call metrics"""
        self._counters["api_calls_total"] += 1
        self._histograms["api_latency"].append(duration_ms)
        
        if status_code >= 400:
            self._counters["api_errors"] += 1
    
    # ML Metrics
    def record_prediction(self, model: str, confidence: float, actual_value: Optional[float] = None) -> None:
        """Record ML prediction metric"""
        metric = BusinessMetric(
            name="ml_prediction",
            value=confidence,
            category="ml",
            metadata={"model": model, "actual": actual_value}
        )
        self._metrics["predictions"].append(metric)
    
    def record_model_accuracy(self, model: str, accuracy: float) -> None:
        """Record model accuracy"""
        self._gauges[f"model_accuracy_{model}"] = accuracy
    
    # Gauge operations
    def set_gauge(self, name: str, value: float) -> None:
        """Set gauge value"""
        self._gauges[name] = value
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment counter"""
        self._counters[name] += value
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        return {
            "counters": dict(self._counters),
            "gauges": self._gauges,
            "histograms": {
                name: {
                    "count": len(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                }
                for name, values in self._histograms.items()
            },
            "business_metrics": {
                category: len(metrics)
                for category, metrics in self._metrics.items()
            }
        }
    
    async def get_latest_metrics(self, category: Optional[str] = None) -> list:
        """Get latest metrics filtered by category"""
        async with self._lock:
            all_metrics = []
            for metrics in self._metrics.values():
                all_metrics.extend(metrics)
            
            if category:
                all_metrics = [m for m in all_metrics if m.category == category]
            
            return sorted(all_metrics, key=lambda x: x.timestamp, reverse=True)[:100]
  
