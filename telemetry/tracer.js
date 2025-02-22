// orbital-agent/src/telemetry/tracer.js
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');

class DistributedTracer {
  constructor(serviceName) {
    this.provider = new NodeTracerProvider();
    this.exporter = new OTLPTraceExporter();
    
    this.provider.addSpanProcessor(
      new BatchSpanProcessor(this.exporter, {
        maxQueueSize: 1000,
        scheduledDelayMillis: 3000,
      })
    );
    
    this.provider.register();
  }

  createSpan(name, context) {
    const tracer = this.provider.getTracer('orbital-tracer');
    return tracer.startSpan(name, {}, context);
  }
}
