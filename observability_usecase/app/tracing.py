from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.trace.export import BatchSpanProcessor

resource = Resource.create({
    "service.name":"fraud-api"
})

provider = TracerProvider(resource=resource)

processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://tempo:4317",
                     insecure=True)
)

provider.add_span_processor(processor)

trace.set_tracer_provider(provider)