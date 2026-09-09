import logging
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record):

        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,

            # Injected automatically by OpenTelemetry
            "trace_id": getattr(record, "otelTraceID", None),
            "span_id": getattr(record, "otelSpanID", None),
            "service_name": getattr(record, "otelServiceName", "payment-service"),
        }

        # Include any custom fields passed via extra={}
        reserved = logging.LogRecord("", 0, "", 0, "", (), None).__dict__

        for key, value in record.__dict__.items():
            if key not in reserved:
                log[key] = value

        return json.dumps(log)


def setup_logger():

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()

    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)