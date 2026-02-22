"""
Notification channel implementations
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp


@dataclass
class NotificationChannel:
    """Base notification channel"""
    name: str
    enabled: bool = True
    
    async def send(self, alert: Any) -> bool:
        """Send notification"""
        raise NotImplementedError


class EmailChannel(NotificationChannel):
    """Email notification channel"""
    
    def __init__(self, name: str, smtp_host: str, smtp_port: int,
                 username: str, password: str, from_addr: str, 
                 to_addrs: list, **kwargs):
        super().__init__(name, **kwargs)
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
    
    async def send(self, alert: Any) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.rule_name}"
            
            body = f"""
            Alert: {alert.rule_name}
            Severity: {alert.severity.value}
            Time: {alert.timestamp}
            Message: {alert.message}
            Value: {alert.value}
            
            Labels: {json.dumps(alert.labels, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Run SMTP in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
    
    def _send_email(self, msg: MIMEMultipart) -> None:
        """Send email synchronously"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


class SlackChannel(NotificationChannel):
    """Slack webhook notification channel"""
    
    def __init__(self, name: str, webhook_url: str, channel: str = None, **kwargs):
        super().__init__(name, **kwargs)
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send(self, alert: Any) -> bool:
        """Send Slack notification"""
        try:
            color = {
                "info": "#36a64f",
                "warning": "#ff9900", 
                "error": "#ff0000",
                "critical": "#990000"
            }.get(alert.severity.value, "#808080")
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"{alert.severity.value.upper()}: {alert.rule_name}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Value", "value": str(alert.value), "short": True},
                        {"title": "Time", "value": str(alert.timestamp), "short": True}
                    ],
                    "footer": "WealthHive Monitoring",
                    "ts": alert.timestamp.timestamp()
                }]
            }
            
            if self.channel:
                payload["channel"] = self.channel
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 200
        
        except Exception as e:
            print(f"Slack send failed: {e}")
            return False


class WebhookChannel(NotificationChannel):
    """Generic webhook notification channel"""
    
    def __init__(self, name: str, url: str, headers: Dict[str, str] = None,
                 method: str = "POST", **kwargs):
        super().__init__(name, **kwargs)
        self.url = url
        self.headers = headers or {}
        self.method = method
    
    async def send(self, alert: Any) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "value": alert.value,
                "labels": alert.labels,
                "status": alert.status.value
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method, 
                    self.url, 
                    json=payload,
                    headers=self.headers
                ) as response:
                    return 200 <= response.status < 300
        
        except Exception as e:
            print(f"Webhook send failed: {e}")
            return False


class PagerDutyChannel(NotificationChannel):
    """PagerDuty integration channel"""
    
    def __init__(self, name: str, routing_key: str, **kwargs):
        super().__init__(name, **kwargs)
        self.routing_key = routing_key
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
    
    async def send(self, alert: Any) -> bool:
        """Send PagerDuty event"""
        try:
            severity_map = {
                "critical": "critical",
                "error": "error", 
                "warning": "warning",
                "info": "info"
            }
            
            payload = {
                "routing_key": self.routing_key,
                "event_action": "trigger",
                "dedup_key": alert.id,
                "payload": {
                    "summary": alert.message,
                    "severity": severity_map.get(alert.severity.value, "warning"),
                    "source": alert.rule_name,
                    "custom_details": {
                        "value": alert.value,
                        "labels": alert.labels
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload) as response:
                    return response.status == 202
        
        except Exception as e:
            print(f"PagerDuty send failed: {e}")
            return False
          
