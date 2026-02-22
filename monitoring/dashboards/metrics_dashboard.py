"""
Real-time metrics dashboard
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str]


class MetricsDashboard:
    """
    Real-time metrics visualization
    """
    
    def __init__(self, retention_minutes: int = 60):
        self.retention = retention_minutes
        self._metrics: Dict[str, List[MetricPoint]] = {}
        self._lock = asyncio.Lock()
    
    async def record(self, metric_name: str, value: float, 
                     labels: Dict[str, str] = None) -> None:
        """Record metric point"""
        async with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = []
            
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                labels=labels or {}
            )
            
            self._metrics[metric_name].append(point)
            
            # Cleanup old data
            cutoff = datetime.utcnow() - timedelta(minutes=self.retention)
            self._metrics[metric_name] = [
                p for p in self._metrics[metric_name] 
                if p.timestamp > cutoff
            ]
    
    def get_time_series(self, metric_name: str, 
                       start: datetime = None,
                       end: datetime = None) -> List[Dict]:
        """Get time series data"""
        if metric_name not in self._metrics:
            return []
        
        points = self._metrics[metric_name]
        
        if start:
            points = [p for p in points if p.timestamp >= start]
        if end:
            points = [p for p in points if p.timestamp <= end]
        
        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "value": p.value,
                "labels": p.labels
            }
            for p in sorted(points, key=lambda x: x.timestamp)
        ]
    
    def get_gauge(self, metric_name: str) -> Optional[float]:
        """Get latest gauge value"""
        if metric_name not in self._metrics:
            return None
        
        points = self._metrics[metric_name]
        return points[-1].value if points else None
    
    def get_counter_rate(self, metric_name: str, 
                        window_minutes: int = 5) -> float:
        """Get counter rate per minute"""
        if metric_name not in self._metrics:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = [p for p in self._metrics[metric_name] if p.timestamp > cutoff]
        
        if len(recent) < 2:
            return 0.0
        
        values = [p.value for p in recent]
        total_increase = values[-1] - values[0]
        time_span = (recent[-1].timestamp - recent[0].timestamp).total_seconds() / 60
        
        return total_increase / time_span if time_span > 0 else 0.0
    
    def get_histogram(self, metric_name: str, 
                     buckets: List[float] = None) -> Dict[str, int]:
        """Get histogram distribution"""
        if metric_name not in self._metrics:
            return {}
        
        values = [p.value for p in self._metrics[metric_name]]
        
        if not buckets:
            buckets = [10, 50, 100, 500, 1000, 5000]
        
        distribution = {}
        for i, bucket in enumerate(buckets):
            count = sum(1 for v in values if v <= bucket)
            distribution[f"le_{bucket}"] = count
        
        distribution["+Inf"] = len(values)
        
        return distribution
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "metrics_count": len(self._metrics),
            "total_datapoints": sum(len(points) for points in self._metrics.values()),
            "metrics": list(self._metrics.keys())
        }
      
