"""
ML model monitoring dashboard
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import deque


@dataclass
class ModelMetrics:
    """ML model metrics"""
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_ms: float
    predictions_count: int
    last_updated: datetime


class MLDashboard:
    """
    ML model performance monitoring
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._models: Dict[str, ModelMetrics] = {}
        self._predictions: Dict[str, deque] = {}
        self._drift_metrics: Dict[str, List[Dict]] = {}
    
    def register_model(self, name: str, version: str) -> None:
        """Register model for monitoring"""
        self._models[name] = ModelMetrics(
            model_name=name,
            version=version,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            latency_ms=0.0,
            predictions_count=0,
            last_updated=datetime.utcnow()
        )
        self._predictions[name] = deque(maxlen=self.max_history)
        self._drift_metrics[name] = []
    
    def record_prediction(self, model_name: str, 
                         confidence: float,
                         actual: Optional[float] = None,
                         latency_ms: float = 0,
                         features: Dict = None) -> None:
        """Record prediction"""
        if model_name not in self._predictions:
            self.register_model(model_name, "unknown")
        
        self._predictions[model_name].append({
            "timestamp": datetime.utcnow().isoformat(),
            "confidence": confidence,
            "actual": actual,
            "latency_ms": latency_ms,
            "features": features or {}
        })
        
        # Update latency
        if model_name in self._models:
            current = self._models[model_name]
            current.latency_ms = (
                (current.latency_ms * current.predictions_count + latency_ms) /
                (current.predictions_count + 1)
            )
            current.predictions_count += 1
            current.last_updated = datetime.utcnow()
    
    def update_model_metrics(self, model_name: str,
                            accuracy: float = None,
                            precision: float = None,
                            recall: float = None,
                            f1_score: float = None) -> None:
        """Update model performance metrics"""
        if model_name not in self._models:
            return
        
        model = self._models[model_name]
        if accuracy is not None:
            model.accuracy = accuracy
        if precision is not None:
            model.precision = precision
        if recall is not None:
            model.recall = recall
        if f1_score is not None:
            model.f1_score = f1_score
        
        model.last_updated = datetime.utcnow()
    
    def record_drift(self, model_name: str, 
                     drift_score: float,
                     feature_name: str = None) -> None:
        """Record data drift detection"""
        if model_name not in self._drift_metrics:
            self._drift_metrics[model_name] = []
        
        self._drift_metrics[model_name].append({
            "timestamp": datetime.utcnow().isoformat(),
            "drift_score": drift_score,
            "feature": feature_name,
            "alert": drift_score > 0.5
        })
    
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Get model status"""
        if model_name not in self._models:
            return {"error": "Model not found"}
        
        model = self._models[model_name]
        predictions = list(self._predictions.get(model_name, []))
        
        # Calculate recent accuracy if actuals available
        recent = predictions[-100:] if predictions else []
        actuals = [p for p in recent if p["actual"] is not None]
        
        return {
            "name": model.model_name,
            "version": model.version,
            "metrics": {
                "accuracy": model.accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1_score": model.f1_score,
                "avg_latency_ms": model.latency_ms,
                "total_predictions": model.predictions_count
            },
            "recent_predictions": len(predictions),
            "with_actuals": len(actuals),
            "last_updated": model.last_updated.isoformat(),
            "health": self._calculate_health(model)
        }
    
    def _calculate_health(self, model: ModelMetrics) -> str:
        """Calculate model health"""
        if model.accuracy < 0.5:
            return "critical"
        elif model.accuracy < 0.7:
            return "warning"
        elif model.latency_ms > 1000:
            return "degraded"
        return "healthy"
    
    def get_all_models(self) -> List[Dict]:
        """Get all model statuses"""
        return [self.get_model_status(name) for name in self._models.keys()]
    
    def get_drift_report(self, model_name: str) -> List[Dict]:
        """Get drift detection report"""
        return self._drift_metrics.get(model_name, [])
    
    def get_feature_importance(self, model_name: str) -> Dict[str, float]:
        """Get feature importance (placeholder)"""
        # Would integrate with actual model
        return {}
      
