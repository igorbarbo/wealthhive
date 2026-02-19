"""
Trading strategy domain entity
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


@dataclass
class Strategy:
    """Trading strategy entity"""
    name: str
    description: str
    strategy_type: str  # moving_average, momentum, mean_reversion, ml
    id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None  # None for system strategies
    parameters: Dict[str Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """Update strategy parameters"""
        self.parameters.update(new_params)
        self.updated_at = datetime.utcnow()
    
    def record_performance(
        self,
        sharpe_ratio: float,
        total_return: float,
        max_drawdown: float,
    ) -> None:
        """Record backtest/live performance"""
        self.performance_metrics = {
            "sharpe_ratio": sharpe_ratio,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "recorded_at": datetime.utcnow().isoformat(),
        }
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate strategy"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def validate_parameters(self) -> List[str]:
        """Validate strategy parameters, return list of errors"""
        errors = []
        
        if self.strategy_type == "moving_average":
            required = ["short_window", "long_window"]
        elif self.strategy_type == "momentum":
            required = ["lookback_period", "threshold"]
        elif self.strategy_type == "mean_reversion":
            required = ["lookback_period", "std_dev_threshold"]
        else:
            return errors
        
        for param in required:
            if param not in self.parameters:
                errors.append(f"Missing required parameter: {param}")
        
        return errors
