# src/telemetry/metrics_collector.py
import time
import psutil
from typing import Dict
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

class SystemMetrics:
    def __init__(self, registry: CollectorRegistry):
        self.cpu_usage = Gauge('system_cpu_percent', 'CPU usage', registry=registry)
        self.memory_usage = Gauge('system_memory_percent', 'Memory usage', registry=registry)
        
    def update(self) -> None:
        self.cpu_usage.set(psutil.cpu_percent())
        self.memory_usage.set(psutil.virtual_memory().percent)

class ServiceMetrics:
    def __init__(self, registry: CollectorRegistry):
        self.request_count = Gauge('service_requests_total', 'Total requests', registry=registry)
        self.error_count = Gauge('service_errors_total', 'Total errors', registry=registry)
        
    def increment_requests(self) -> None:
        self.request_count.inc()
        
    def increment_errors(self) -> None:
        self.error_count.inc()

class MetricsPusher:
    def __init__(self, gateway: str):
        self.registry = CollectorRegistry()
        self.gateway = gateway
        self.system = SystemMetrics(self.registry)
        self.service = ServiceMetrics(self.registry)
        
    def push(self) -> None:
        self.system.update()
        push_to_gateway(self.gateway, job='orbital_agent', registry=self.registry)
