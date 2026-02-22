"""
Log aggregation and analysis
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    logger: str
    message: str
    correlation_id: Optional[str]
    context: Dict[str, Any]
    metadata: Dict[str, Any]


class LogAggregator:
    """
    Aggregate and analyze logs
    """
    
    def __init__(self, retention_hours: int = 24):
        self.retention = retention_hours
        self._logs: List[LogEntry] = []
        self._index: Dict[str, List[LogEntry]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def ingest(self, log_data: Dict[str, Any]) -> None:
        """Ingest log entry"""
        entry = LogEntry(
            timestamp=datetime.fromisoformat(log_data.get("timestamp", datetime.utcnow().isoformat())),
            level=log_data.get("level", "info"),
            logger=log_data.get("logger", "unknown"),
            message=log_data.get("message", ""),
            correlation_id=log_data.get("correlation_id"),
            context=log_data.get("context", {}),
            metadata={k: v for k, v in log_data.items() 
                     if k not in ["timestamp", "level", "logger", "message", "correlation_id", "context"]}
        )
        
        async with self._lock:
            self._logs.append(entry)
            self._index[entry.logger].append(entry)
            if entry.correlation_id:
                self._index[f"corr:{entry.correlation_id}"].append(entry)
            
            # Cleanup old logs
            await self._cleanup()
    
    async def _cleanup(self) -> None:
        """Remove old logs"""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention)
        self._logs = [l for l in self._logs if l.timestamp > cutoff]
        
        # Rebuild index
        self._index.clear()
        for log in self._logs:
            self._index[log.logger].append(log)
            if log.correlation_id:
                self._index[f"corr:{log.correlation_id}"].append(log)
    
    def search(self, query: str = None, level: str = None,
               logger: str = None, correlation_id: str = None,
               start_time: datetime = None, end_time: datetime = None,
               limit: int = 100) -> List[LogEntry]:
        """Search logs"""
        results = self._logs
        
        if logger:
            results = self._index.get(logger, [])
        
        if correlation_id:
            results = self._index.get(f"corr:{correlation_id}", [])
        
        if query:
            results = [l for l in results if query.lower() in l.message.lower()]
        
        if level:
            results = [l for l in results if l.level == level]
        
        if start_time:
            results = [l for l in results if l.timestamp >= start_time]
        
        if end_time:
            results = [l for l in results if l.timestamp <= end_time]
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_stats(self, hours: int = 1) -> Dict[str, Any]:
        """Get log statistics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [l for l in self._logs if l.timestamp > cutoff]
        
        level_counts = defaultdict(int)
        logger_counts = defaultdict(int)
        
        for log in recent:
            level_counts[log.level] += 1
            logger_counts[log.logger] += 1
        
        return {
            "total_logs": len(recent),
            "by_level": dict(level_counts),
            "by_logger": dict(logger_counts),
            "error_rate": level_counts.get("error", 0) / len(recent) if recent else 0,
            "unique_correlation_ids": len(set(l.correlation_id for l in recent if l.correlation_id))
        }
    
    def get_trace(self, correlation_id: str) -> List[LogEntry]:
        """Get all logs for a correlation ID"""
        return sorted(
            self._index.get(f"corr:{correlation_id}", []),
            key=lambda x: x.timestamp
        )
    
    def find_errors(self, limit: int = 50) -> List[LogEntry]:
        """Find recent errors"""
        errors = [l for l in self._logs if l.level in ["error", "critical"]]
        return sorted(errors, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def export_logs(self, format: str = "json") -> str:
        """Export logs to string"""
        import json
        
        if format == "json":
            return json.dumps([
                {
                    "timestamp": l.timestamp.isoformat(),
                    "level": l.level,
                    "logger": l.logger,
                    "message": l.message,
                    "correlation_id": l.correlation_id,
                    "context": l.context
                }
                for l in sorted(self._logs, key=lambda x: x.timestamp)
            ], indent=2)
        
        # Plain text format
        lines = []
        for l in sorted(self._logs, key=lambda x: x.timestamp):
            lines.append(f"[{l.timestamp}] {l.level.upper()} {l.logger}: {l.message}")
        return '\n'.join(lines)
      
