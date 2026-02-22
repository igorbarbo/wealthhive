"""
Prometheus metrics exporter
"""

from typing import Any, Dict, List
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json


class PrometheusExporter:
    """
    Export metrics in Prometheus format
    """
    
    def __init__(self, port: int = 9090):
        self.port = port
        self._registry: Dict[str, Any] = {}
        self._server: HTTPServer = None
        self._thread: threading.Thread = None
    
    def register_metric(self, name: str, help_text: str, metric_type: str = "gauge") -> None:
        """Register a metric with Prometheus"""
        self._registry[name] = {
            "help": help_text,
            "type": metric_type,
            "values": []
        }
    
    def set_metric(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Set metric value"""
        if name not in self._registry:
            self.register_metric(name, f"Metric {name}")
        
        self._registry[name]["values"].append({
            "value": value,
            "labels": labels or {},
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def start_server(self) -> None:
        """Start Prometheus HTTP server"""
        handler = self._create_handler()
        self._server = HTTPServer(('', self.port), handler)
        self._thread = threading.Thread(target=self._server.serve_forever)
        self._thread.daemon = True
        self._thread.start()
        print(f"Prometheus exporter started on port {self.port}")
    
    def stop_server(self) -> None:
        """Stop Prometheus server"""
        if self._server:
            self._server.shutdown()
            self._thread.join()
    
    def _create_handler(self):
        """Create HTTP request handler"""
        registry = self._registry
        
        class PrometheusHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/metrics':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    
                    output = []
                    for name, data in registry.items():
                        output.append(f"# HELP {name} {data['help']}")
                        output.append(f"# TYPE {name} {data['type']}")
                        
                        for value_data in data['values'][-10:]:  # Last 10 values
                            labels_str = ""
                            if value_data['labels']:
                                labels = [f'{k}="{v}"' for k, v in value_data['labels'].items()]
                                labels_str = "{" + ",".join(labels) + "}"
                            
                            output.append(f"{name}{labels_str} {value_data['value']}")
                    
                    self.wfile.write('\n'.join(output).encode())
                
                elif self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "healthy"}).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress logs
        
        return PrometheusHandler
    
    def export_metrics(self) -> str:
        """Export metrics as Prometheus format string"""
        lines = []
        for name, data in self._registry.items():
            lines.append(f"# HELP {name} {data['help']}")
            lines.append(f"# TYPE {name} {data['type']}")
            for value_data in data['values'][-5:]:
                lines.append(f"{name} {value_data['value']}")
        return '\n'.join(lines)
      
