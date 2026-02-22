"""
Health check HTTP endpoints
"""

from typing import Dict, Any
from aiohttp import web
import json


class HealthEndpoint:
    """
    HTTP endpoints for health checks
    """
    
    def __init__(self, health_checker):
        self.checker = health_checker
    
    def setup_routes(self, app: web.Application) -> None:
        """Setup health routes"""
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/health/live', self.liveness_check)
        app.router.add_get('/health/ready', self.readiness_check)
        app.router.add_get('/health/detailed', self.detailed_health)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Basic health check"""
        status = self.checker.get_overall_status()
        
        code = 200 if status == HealthStatus.HEALTHY else 503
        
        return web.json_response(
            {"status": status.value},
            status=code
        )
    
    async def liveness_check(self, request: web.Request) -> web.Response:
        """Kubernetes liveness probe"""
        return web.json_response({"alive": True})
    
    async def readiness_check(self, request: web.Request) -> web.Response:
        """Kubernetes readiness probe"""
        await self.checker.check_all()
        status = self.checker.get_overall_status()
        
        if status == HealthStatus.UNHEALTHY:
            return web.json_response(
                {"ready": False, "status": status.value},
                status=503
            )
        
        return web.json_response({"ready": True, "status": status.value})
    
    async def detailed_health(self, request: web.Request) -> web.Response:
        """Detailed health report"""
        await self.checker.check_all()
        report = self.checker.get_health_report()
        
        status_code = 200 if report["status"] == "healthy" else 503
        
        return web.json_response(report, status=status_code)
      
