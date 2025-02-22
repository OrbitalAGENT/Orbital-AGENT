// orbital-agent/src/telemetry/metrics.rs
use prometheus::{CounterVec, Encoder, GaugeVec, Opts, Registry, TextEncoder};
use std::error::Error;

pub struct MetricsCollector {
    requests: CounterVec,
    latency: GaugeVec,
    registry: Registry,
}

impl MetricsCollector {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        let requests = CounterVec::new(
            Opts::new("http_requests", "Total HTTP requests"),
            &["method", "endpoint"],
        )?;
        
        let latency = GaugeVec::new(
            Opts::new("request_latency", "Request latency in seconds"),
            &["endpoint"],
        )?;
        
        let registry = Registry::new();
        registry.register(requests.clone())?;
        registry.register(latency.clone())?;
        
        Ok(MetricsCollector { requests, latency, registry })
    }

    pub fn record_request(&self, method: &str, endpoint: &str) {
        self.requests.with_label_values(&[method, endpoint]).inc();
    }

    pub fn record_latency(&self, endpoint: &str, duration: f64) {
        self.latency.with_label_values(&[endpoint]).set(duration);
    }

    pub fn export_metrics(&self) -> Result<String, Box<dyn Error>> {
        let encoder = TextEncoder::new();
        let mut buffer = Vec::new();
        encoder.encode(&self.registry.gather(), &mut buffer)?;
        Ok(String::from_utf8(buffer)?)
    }
}
