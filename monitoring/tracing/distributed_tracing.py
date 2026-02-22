"""
Distributed tracing for microservices
"""

import uuid
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from contextvars import ContextVar


@dataclass
class Span:
    """Trace span"""
    span_id: str
    trace_id: str
    parent_id: Optional[str]
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict] = field(default_factory=list)
    
    def finish(self, tags: Dict[str, str] = None) -> None:
        """Finish span"""
        self.end_time = datetime.utcnow()
        if tags:
            self.tags.update(tags)
    
    def log_event(self, event: str, payload: Dict = None) -> None:
        """Log event in span"""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "payload": payload or {}
        })
    
    def set_tag(self, key: str, value: str) -> None:
        """Set tag"""
        self.tags[key] = value
    
    def duration_ms(self) -> float:
        """Get duration in milliseconds"""
        if not self.end_time:
            return 0
        return (self.end_time - self.start_time).total_seconds() * 1000


@dataclass
class TraceContext:
    """Trace context for request"""
    trace_id: str
    span_id: str
    sampled: bool = True
    
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers"""
        return {
            "X-Trace-Id": self.trace_id,
            "X-Span-Id": self.span_id,
            "X-Sampled": "1" if self.sampled else "0"
        }
    
    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "TraceContext":
        """Create from HTTP headers"""
        return cls(
            trace_id=headers.get("X-Trace-Id", str(uuid.uuid4())),
            span_id=headers.get("X-Span-Id", str(uuid.uuid4())),
            sampled=headers.get("X-Sampled", "1") == "1"
        )


class DistributedTracer:
    """
    Distributed tracing implementation
    """
    
    _current_span: ContextVar[Optional[Span]] = ContextVar('current_span', default=None)
    
    def __init__(self, service_name: str, sample_rate: float = 1.0):
        self.service_name = service_name
        self.sample_rate = sample_rate
        self._spans: List[Span] = []
        self._exporters: List[Any] = []
    
    def start_span(self, name: str, parent: Span = None,
                   tags: Dict[str, str] = None) -> Span:
        """Start new span"""
        trace_id = parent.trace_id if parent else str(uuid.uuid4())
        parent_id = parent.span_id if parent else None
        
        span = Span(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            parent_id=parent_id,
            name=name,
            start_time=datetime.utcnow(),
            tags={"service": self.service_name, **(tags or {})}
        )
        
        self._current_span.set(span)
        self._spans.append(span)
        
        return span
    
    def finish_span(self, span: Span, tags: Dict[str, str] = None) -> None:
        """Finish span"""
        span.finish(tags)
        self._export_span(span)
    
    def get_current_span(self) -> Optional[Span]:
        """Get current active span"""
        return self._current_span.get()
    
    def start_trace(self, name: str, context: TraceContext = None) -> Span:
        """Start new trace"""
        if context is None:
            context = TraceContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4())
            )
        
        return self.start_span(name, tags={"trace.id": context.trace_id})
    
    def inject_context(self, carrier: Dict[str, str]) -> None:
        """Inject trace context into carrier"""
        current = self.get_current_span()
        if current:
            carrier["X-Trace-Id"] = current.trace_id
            carrier["X-Span-Id"] = current.span_id
    
    def extract_context(self, carrier: Dict[str, str]) -> TraceContext:
        """Extract trace context from carrier"""
        return TraceContext.from_headers(carrier)
    
    def _export_span(self, span: Span) -> None:
        """Export span to backends"""
        for exporter in self._exporters:
            try:
                exporter.export(span)
            except Exception as e:
                print(f"Export error: {e}")
    
    def add_exporter(self, exporter: Any) -> None:
        """Add span exporter"""
        self._exporters.append(exporter)
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for trace"""
        return [s for s in self._spans if s.trace_id == trace_id]
    
    def get_slow_spans(self, threshold_ms: float = 1000) -> List[Span]:
        """Get spans slower than threshold"""
        return [s for s in self._spans if s.duration_ms() > threshold_ms]
    
    def clear(self) -> None:
        """Clear all spans"""
        self._spans.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracing statistics"""
        if not self._spans:
            return {}
        
        durations = [s.duration_ms() for s in self._spans if s.end_time]
        
        return {
            "total_spans": len(self._spans),
            "active_spans": len([s for s in self._spans if not s.end_time]),
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "traces": len(set(s.trace_id for s in self._spans))
        }


class JaegerExporter:
    """Jaeger tracing exporter"""
    
    def __init__(self, agent_host: str = "localhost", agent_port: int = 6831):
        self.agent_host = agent_host
        self.agent_port = agent_port
    
    def export(self, span: Span) -> None:
        """Export span to Jaeger"""
        # Implementation would use jaeger-client
        pass


class ZipkinExporter:
    """Zipkin tracing exporter"""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
    
    def export(self, span: Span) -> None:
        """Export span to Zipkin"""
        # Implementation would send HTTP request to Zipkin
        pass
      
