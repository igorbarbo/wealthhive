"""
Alert rule definitions
"""

from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComparisonOperator(Enum):
    """Comparison operators"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_EQUAL = "ge"
    LESS_EQUAL = "le"


@dataclass
class AlertCondition:
    """Alert condition configuration"""
    metric: str
    operator: ComparisonOperator
    threshold: float
    duration: int = 0  # Duration in seconds condition must be true
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """
    Alert rule definition
    """
    name: str
    condition: AlertCondition
    severity: AlertSeverity
    message: str
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    cooldown: int = 300  # Seconds between alerts
    
    def __post_init__(self):
        self.current_value: float = 0.0
        self.last_triggered: Optional[datetime] = None
        self.condition_met_since: Optional[datetime] = None
    
    def evaluate(self, metric_value: float) -> bool:
        """Evaluate rule against metric value"""
        self.current_value = metric_value
        
        # Check cooldown
        if self.last_triggered:
            if datetime.utcnow() - self.last_triggered < timedelta(seconds=self.cooldown):
                return False
        
        # Evaluate condition
        triggered = self._compare(metric_value)
        
        if triggered:
            if self.condition.duration > 0:
                # Check duration
                if self.condition_met_since is None:
                    self.condition_met_since = datetime.utcnow()
                    return False
                
                elapsed = (datetime.utcnow() - self.condition_met_since).total_seconds()
                if elapsed >= self.condition.duration:
                    self.last_triggered = datetime.utcnow()
                    self.condition_met_since = None
                    return True
                return False
            else:
                self.last_triggered = datetime.utcnow()
                return True
        else:
            self.condition_met_since = None
            return False
    
    def _compare(self, value: float) -> bool:
        """Compare value against threshold"""
        op = self.condition.operator
        
        if op == ComparisonOperator.GREATER_THAN:
            return value > self.condition.threshold
        elif op == ComparisonOperator.LESS_THAN:
            return value < self.condition.threshold
        elif op == ComparisonOperator.EQUAL:
            return value == self.condition.threshold
        elif op == ComparisonOperator.NOT_EQUAL:
            return value != self.condition.threshold
        elif op == ComparisonOperator.GREATER_EQUAL:
            return value >= self.condition.threshold
        elif op == ComparisonOperator.LESS_EQUAL:
            return value <= self.condition.threshold
        
        return False


class ThresholdRule(AlertRule):
    """Simple threshold-based rule"""
    pass


class AnomalyRule(AlertRule):
    """Anomaly detection rule"""
    
    def __init__(self, name: str, metric: str, severity: AlertSeverity, 
                 message: str, std_dev_threshold: float = 3.0, **kwargs):
        condition = AlertCondition(
            metric=metric,
            operator=ComparisonOperator.GREATER_THAN,
            threshold=std_dev_threshold
        )
        super().__init__(name, condition, severity, message, **kwargs)
        self.history: list = []
        self.window_size: int = 100
    
    def evaluate(self, metric_value: float) -> bool:
        """Evaluate using statistical anomaly detection"""
        self.history.append(metric_value)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        if len(self.history) < 10:
            return False
        
        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return False
        
        z_score = abs(metric_value - mean) / std_dev
        self.current_value = z_score
        
        return z_score > self.condition.threshold


class AggregationRule(AlertRule):
    """Rule based on aggregated metrics"""
    
    def __init__(self, name: str, metric: str, severity: AlertSeverity,
                 message: str, aggregation: str = "avg", period_minutes: int = 5, **kwargs):
        condition = AlertCondition(metric=metric, operator=ComparisonOperator.GREATER_THAN, threshold=0)
        super().__init__(name, condition, severity, message, **kwargs)
        self.aggregation = aggregation  # avg, sum, min, max, count
        self.period = period_minutes
        self.data_points: list = []
    
    def add_data_point(self, value: float, timestamp: datetime = None) -> None:
        """Add data point for aggregation"""
        ts = timestamp or datetime.utcnow()
        self.data_points.append((ts, value))
        
        # Clean old data
        cutoff = datetime.utcnow() - timedelta(minutes=self.period)
        self.data_points = [(t, v) for t, v in self.data_points if t > cutoff]
    
    def evaluate(self, metric_value: float = None) -> bool:
        """Evaluate based on aggregated value"""
        if not self.data_points:
            return False
        
        values = [v for _, v in self.data_points]
        
        if self.aggregation == "avg":
            aggregated = sum(values) / len(values)
        elif self.aggregation == "sum":
            aggregated = sum(values)
        elif self.aggregation == "min":
            aggregated = min(values)
        elif self.aggregation == "max":
            aggregated = max(values)
        elif self.aggregation == "count":
            aggregated = len(values)
        else:
            aggregated = values[-1] if values else 0
        
        return self._compare(aggregated)
                   
