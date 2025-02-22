# src/observability/trace_manager.py
import opentelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

class TracingSystem:
    def __init__(self, endpoint: str, service_name: str):
        provider = TracerProvider()
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(service_name)
        
    def start_span(self, name: str) -> opentelemetry.trace.Span:
        return self.tracer.start_span(name)
    
    def add_event(self, span: opentelemetry.trace.Span, name: str, attributes: dict) -> None:
        span.add_event(name, attributes=attributes)
    
    def end_span(self, span: opentelemetry.trace.Span) -> None:
        span.end()
