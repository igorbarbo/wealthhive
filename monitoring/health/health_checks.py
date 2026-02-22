"""
Health check implementations
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import time


class HealthStatus(Enum):
    """Health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Health check result"""
    name: str
    status: HealthStatus
    response_time_ms: float
    timestamp: datetime
    message: str = ""
    metadata: Dict[str, Any] = None


class HealthChecker:
    """
    System health checker
    """
    
    def __init__(self):
        self._checks: Dict[str, Callable] = {}
        self._results: Dict[str, HealthCheck] = {}
        self._lock = asyncio.Lock()
    
    def register_check(self, name: str, check_fn: Callable, 
                       critical: bool = False) -> None:
        """Register health check"""
        self._checks[name] = {
            "fn": check_fn,
            "critical": critical
        }
    
    async def check_all(self) -> Dict[str, HealthCheck]:
        """Run all health checks"""
        results = {}
        
        for name, config in self._checks.items():
            start = time.time()
            try:
                if asyncio.iscoroutinefunction(config["fn"]):
                    healthy = await config["fn"]()
                else:
                    healthy = config["fn"]()
                
                duration = (time.time() - start) * 1000
                
                status = HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY
                
                results[name] = HealthCheck(
                    name=name,
                    status=status,
                    response_time_ms=duration,
                    timestamp=datetime.utcnow(),
                    message="OK" if healthy else "Check failed"
                )
                
            except Exception as e:
                duration = (time.time() - start) * 1000
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=duration,
                    timestamp=datetime.utcnow(),
                    message=str(e)
                )
        
        async with self._lock:
            self._results = results
        
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health"""
        if not self._results:
            return HealthStatus.UNHEALTHY
        
        critical_failed = any(
            r.status == HealthStatus.UNHEALTHY 
            for name, r in self._results.items()
            if self._checks[name]["critical"]
        )
        
        if critical_failed:
            return HealthStatus.UNHEALTHY
        
        any_unhealthy = any(r.status == HealthStatus.UNHEALTHY for r in self._results.values())
        if any_unhealthy:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get full health report"""
        return {
            "status": self.get_overall_status().value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                name: {
                    "status": check.status.value,
                    "response_time_ms": check.response_time_ms,
                    "message": check.message
                }
                for name, check in self._results.items()
            }
        }
    
    # Built-in health checks
    
    async def check_database(self, db_pool) -> bool:
        """Check database connectivity"""
        try:
            # Execute simple query
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def check_redis(self, redis_client) -> bool:
        """Check Redis connectivity"""
        try:
            await redis_client.ping()
            return True
        except Exception:
            return False
    
    def check_disk_space(self, threshold_percent: float = 90) -> bool:
        """Check disk space"""
        import shutil
        usage = shutil.disk_usage("/")
        used_percent = (usage.used / usage.total) * 100
        return used_percent < threshold_percent
    
    def check_memory(self, threshold_percent: float = 95) -> bool:
        """Check memory usage"""
        import psutil
        return psutil.virtual_memory().percent < threshold_percent
    
    async def check_external_api(self, url: str, timeout: int = 5) -> bool:
        """Check external API"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as resp:
                    return resp.status < 500
        except Exception:
            return False
          
