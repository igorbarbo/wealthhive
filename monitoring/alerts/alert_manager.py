"""
Central alert management system
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Alert instance"""
    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    labels: Dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


class AlertManager:
    """
    Manage alerts and notifications
    """
    
    def __init__(self):
        self._rules: List[Any] = []
        self._alerts: Dict[str, Alert] = {}
        self._channels: List[Any] = []
        self._handlers: List[Callable] = []
        self._history: List[Alert] = []
        self._lock = asyncio.Lock()
        self._running = False
    
    def add_rule(self, rule: Any) -> None:
        """Add alert rule"""
        self._rules.append(rule)
    
    def add_channel(self, channel: Any) -> None:
        """Add notification channel"""
        self._channels.append(channel)
    
    def register_handler(self, handler: Callable) -> None:
        """Register alert handler callback"""
        self._handlers.append(handler)
    
    async def start(self, check_interval: int = 30) -> None:
        """Start alert monitoring"""
        self._running = True
        while self._running:
            await self._evaluate_rules()
            await asyncio.sleep(check_interval)
    
    def stop(self) -> None:
        """Stop alert monitoring"""
        self._running = False
    
    async def _evaluate_rules(self) -> None:
        """Evaluate all alert rules"""
        for rule in self._rules:
            try:
                triggered = await rule.evaluate() if asyncio.iscoroutinefunction(rule.evaluate) else rule.evaluate()
                
                if triggered:
                    await self._trigger_alert(rule)
                else:
                    await self._resolve_alert(rule.name)
            except Exception as e:
                print(f"Error evaluating rule {rule.name}: {e}")
    
    async def _trigger_alert(self, rule: Any) -> None:
        """Trigger new alert"""
        async with self._lock:
            alert_id = f"{rule.name}_{datetime.utcnow().timestamp()}"
            
            if alert_id in self._alerts:
                return  # Already active
            
            alert = Alert(
                id=alert_id,
                rule_name=rule.name,
                severity=rule.severity,
                message=rule.message,
                timestamp=datetime.utcnow(),
                labels=rule.labels,
                value=rule.current_value if hasattr(rule, 'current_value') else 0.0
            )
            
            self._alerts[alert_id] = alert
            self._history.append(alert)
            
            # Notify channels
            await self._notify_channels(alert)
            
            # Call handlers
            for handler in self._handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    print(f"Handler error: {e}")
    
    async def _resolve_alert(self, rule_name: str) -> None:
        """Resolve alert for rule"""
        async with self._lock:
            to_resolve = [
                alert_id for alert_id, alert in self._alerts.items()
                if alert.rule_name == rule_name and alert.status == AlertStatus.ACTIVE
            ]
            
            for alert_id in to_resolve:
                self._alerts[alert_id].status = AlertStatus.RESOLVED
                self._alerts[alert_id].resolved_at = datetime.utcnow()
    
    async def _notify_channels(self, alert: Alert) -> None:
        """Send alert to all channels"""
        for channel in self._channels:
            try:
                await channel.send(alert) if asyncio.iscoroutinefunction(channel.send) else channel.send(alert)
            except Exception as e:
                print(f"Channel notification error: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge alert"""
        if alert_id in self._alerts:
            self._alerts[alert_id].status = AlertStatus.ACKNOWLEDGED
            self._alerts[alert_id].acknowledged_by = user
            return True
        return False
    
    def silence_alert(self, alert_id: str, duration_minutes: int) -> bool:
        """Silence alert temporarily"""
        if alert_id in self._alerts:
            self._alerts[alert_id].status = AlertStatus.SILENCED
            # Schedule unsilence
            asyncio.create_task(self._unsilence_after(alert_id, duration_minutes))
            return True
        return False
    
    async def _unsilence_after(self, alert_id: str, minutes: int) -> None:
        """Unsilence alert after duration"""
        await asyncio.sleep(minutes * 60)
        if alert_id in self._alerts and self._alerts[alert_id].status == AlertStatus.SILENCED:
            self._alerts[alert_id].status = AlertStatus.ACTIVE
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts"""
        alerts = [a for a in self._alerts.values() if a.status == AlertStatus.ACTIVE]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return sorted(self._history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return {
            "active": len(self.get_active_alerts()),
            "critical": len(self.get_active_alerts(AlertSeverity.CRITICAL)),
            "warning": len(self.get_active_alerts(AlertSeverity.WARNING)),
            "total_24h": len([a for a in self._history 
                           if (datetime.utcnow() - a.timestamp).days < 1])
          }
      
