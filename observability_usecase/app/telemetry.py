from fastapi import FastAPI
import psutil

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource

# Trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


resource = Resource.create({
    "service.name": "payment-service",
    "service.version": "1.0"
})

# ---------- Metrics ----------
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint="http://otel-collector:4317",
        insecure=True
    )
)

metrics.set_meter_provider(
    MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
)

meter = metrics.get_meter("payment-meter")

payment_success_counter = meter.create_counter(
    "payment_success_total"
)

payment_failed_counter = meter.create_counter(
    "payment_failed_total"
)

http_500_counter = meter.create_counter(
    "http_500_total"
)

payment_latency = meter.create_histogram(
    "payment_processing_seconds",
    unit="s"
)

def ram_callback(options):
    return [
        metrics.Observation(
            psutil.virtual_memory().used / 1024 / 1024
        )
    ]

meter.create_observable_gauge(
    name="system_ram_usage_mb",
    callbacks=[ram_callback]
)

# ---------- Setup Function ----------
def setup_telemetry(app: FastAPI):

    tracer_provider = TracerProvider(resource=resource)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="otel-collector:4317",
                insecure=True
            )
        )
    )

    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)