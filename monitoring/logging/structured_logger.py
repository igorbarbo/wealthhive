"""
Structured JSON logging for WealthHive
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger


class LogLevel(Enum):
    """Log levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StructuredLogger:
    """
    Enterprise structured logger with JSON output
    """
    
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_level(level))
        
        # Configure JSON formatter
        log_handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s',
            rename_fields={'levelname': 'level'}
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        
        self.correlation_id: Optional[str] = None
        self.context: Dict[str, Any] = {}
    
    def _get_level(self, level: LogLevel) -> int:
        """Convert LogLevel to logging level"""
        levels = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        return levels.get(level, logging.INFO)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing"""
        self.correlation_id = correlation_id
    
    def add_context(self, key: str, value: Any) -> None:
        """Add persistent context"""
        self.context[key] = value
    
    def clear_context(self) -> None:
        """Clear context"""
        self.context = {}
    
    def _log(self, level: LogLevel, message: str, 
             extra: Dict[str, Any] = None, exc_info: bool = False) -> None:
        """Internal log method"""
        if self._should_log(level):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "logger": self.name,
                "level": level.value,
                "message": message,
                "correlation_id": self.correlation_id,
                "context": self.context,
                **(extra or {})
            }
            
            if exc_info and sys.exc_info()[0]:
                log_data["exception"] = traceback.format_exc()
            
            self.logger.log(
                self._get_level(level),
                json.dumps(log_data),
                extra={"correlation_id": self.correlation_id}
            )
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if level should be logged"""
        levels = list(LogLevel)
        return levels.index(level) >= levels.index(self.level)
    
    def debug(self, message: str, **kwargs) -> None:
        """Debug log"""
        self._log(LogLevel.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Info log"""
        self._log(LogLevel.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Warning log"""
        self._log(LogLevel.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Error log"""
        self._log(LogLevel.ERROR, message, kwargs, exc_info=True)
    
    def critical(self, message: str, **kwargs) -> None:
        """Critical log"""
        self._log(LogLevel.CRITICAL, message, kwargs, exc_info=True)
    
    def log_request(self, method: str, path: str, status_code: int,
                   duration_ms: float, user_id: str = None, **kwargs) -> None:
        """Log HTTP request"""
        self.info(
            f"{method} {path} {status_code}",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            **kwargs
        )
    
    def log_trade(self, trade_id: str, portfolio_id: str, asset: str,
                 action: str, quantity: float, price: float, **kwargs) -> None:
        """Log trade execution"""
        self.info(
            f"Trade executed: {trade_id}",
            event_type="trade",
            trade_id=trade_id,
            portfolio_id=portfolio_id,
            asset=asset,
            action=action,
            quantity=quantity,
            price=price,
            **kwargs
        )
    
    def log_ml_prediction(self, model: str, prediction: float,
                         confidence: float, features: Dict, **kwargs) -> None:
        """Log ML prediction"""
        self.info(
            f"ML prediction from {model}",
            event_type="ml_prediction",
            model=model,
            prediction=prediction,
            confidence=confidence,
            feature_count=len(features),
            **kwargs
        )
    
    def log_security_event(self, event_type: str, user_id: str,
                          details: Dict, severity: LogLevel = LogLevel.WARNING) -> None:
        """Log security event"""
        self._log(
            severity,
            f"Security event: {event_type}",
            event_type="security",
            security_event_type=event_type,
            user_id=user_id,
            details=details
        )
                            
