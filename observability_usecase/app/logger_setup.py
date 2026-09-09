import logging
import sys

from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


def configure_logging():

    # Create OpenTelemetry LoggerProvider
    logger_provider = LoggerProvider()

    # Send logs to OTel Collector
    otlp_exporter = OTLPLogExporter(
        endpoint="otel-collector:4317",
        insecure=True
    )

    # Batch logs before sending
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(otlp_exporter)
    )

    # Register global LoggerProvider
    _logs.set_logger_provider(logger_provider)

    # Bridge standard Python logging -> OpenTelemetry
    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider
    )

    # Configure root Python logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add OpenTelemetry handler
    root_logger.addHandler(handler)

    # Optional: also print logs to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)