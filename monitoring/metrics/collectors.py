"""
Metrics collectors for system and business metrics
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import time
import psutil


@dataclass
class MetricValue:
    """Single metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: str  # counter, gauge, histogram, summary


class MetricsCollector:
    """
    Collect and aggregate system and application metrics
    """
    
    def __init__(self):
        self._metrics: List[MetricValue] = []
        self._collectors: Dict[str, Callable] = {}
        self._lock = asyncio.Lock()
        self._running = False
    
    def register_collector(self, name: str, collector: Callable) -> None:
        """Register a custom metric collector"""
        self._collectors[name] = collector
    
    async def start_collection(self, interval: int = 60) -> None:
        """Start periodic metrics collection"""
        self._running = True
        while self._running:
            await self._collect_all()
            await asyncio.sleep(interval)
    
    def stop_collection(self) -> None:
        """Stop metrics collection"""
        self._running = False
    
    async def _collect_all(self) -> None:
        """Collect all registered metrics"""
        async with self._lock:
            # System metrics
            await self._collect_system_metrics()
            
            # Custom collectors
            for name, collector in self._collectors.items():
                try:
                    value = await collector() if asyncio.iscoroutinefunction(collector) else collector()
                    self._metrics.append(MetricValue(
                        name=name,
                        value=float(value),
                        timestamp=datetime.utcnow(),
                        labels={},
                        metric_type="gauge"
                    ))
                except Exception as e:
                    print(f"Error collecting {name}: {e}")
    
    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self._metrics.append(MetricValue(
            name="system_cpu_usage_percent",
            value=cpu_percent,
            timestamp=datetime.utcnow(),
            labels={"type": "total"},
            metric_type="gauge"
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self._metrics.append(MetricValue(
            name="system_memory_usage_percent",
            value=memory.percent,
            timestamp=datetime.utcnow(),
            labels={"type": "virtual"},
            metric_type="gauge"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self._metrics.append(MetricValue(
            name="system_disk_usage_percent",
            value=(disk.used / disk.total) * 100,
            timestamp=datetime.utcnow(),
            labels={"mount": "/"},
            metric_type="gauge"
        ))
        
        # Network metrics
        net_io = psutil.net_io_counters()
        self._metrics.append(MetricValue(
            name="system_network_bytes_sent",
            value=net_io.bytes_sent,
            timestamp=datetime.utcnow(),
            labels={},
            metric_type="counter"
        ))
        self._metrics.append(MetricValue(
            name="system_network_bytes_recv",
            value=net_io.bytes_recv,
            timestamp=datetime.utcnow(),
            labels={},
            metric_type="counter"
        ))
    
    def get_metrics(self, name: Optional[str] = None) -> List[MetricValue]:
        """Get collected metrics"""
        if name:
            return [m for m in self._metrics if m.name == name]
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics"""
        self._metrics.clear()
    
    def get_latest(self, name: str) -> Optional[MetricValue]:
        """Get latest metric by name"""
        metrics = [m for m in self._metrics if m.name == name]
        return max(metrics, key=lambda x: x.timestamp) if metrics else None
      
