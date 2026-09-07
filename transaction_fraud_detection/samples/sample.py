import os
import json
import structlog
from datetime import datetime
from confluent_kafka import Producer, Consumer, KafkaError
from elasticsearch import Elasticsearch

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# 1. Initialize OpenTelemetry Tracing
resource = Resource.create(attributes={"service.name": "kafka-audit-poc-service"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

#  It intercepts the confluent-kafka library.
# When producing a message, it injects the current trace_id into the Kafka message headers.
# When consuming a message, it extracts that trace_id from the headers so the trace history remains 
# linked across different applications.
ConfluentKafkaInstrumentor().instrument()

# 2. Configure structlog with OpenTelemetry Context Injection
# This is a custom middleware function (processor) for structlog.
# It checks if an active OpenTelemetry trace exists. 
# If it finds one, it extracts the trace_id and span_id and attaches them directly into the log payload
def inject_otel_trace_info(logger, method_name, event_dict):
    """Processor to inject active OpenTelemetry trace and span IDs into structlog."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        ctx = span.get_span_context()
        event_dict["trace_id"] = hex(ctx.trace_id)
        event_dict["span_id"] = hex(ctx.span_id)
    return event_dict

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"), # Automatically adds "timestamp"
        structlog.processors.add_log_level,          # Automatically adds "level"
        inject_otel_trace_info,                      # Custom injection for Otel
        structlog.processors.JSONRenderer()          # Outputs clean JSON strings for ES
    ],
    logger_factory=structlog.PrintLoggerFactory(),     # Standard stdout backend
)

logger = structlog.get_logger()

# 3. Initialize Elasticsearch Client
es_client = Elasticsearch(["http://localhost:9200"])
AUDIT_INDEX = "audit-logs"

#  It uses structlog to print a clean JSON string to the terminal.
#  It takes that exact same JSON object (which now contains the timestamp, log level, message details, 
# and automatically injected trace_id) and uploads it to an Elasticsearch index called audit-logs. 
# Kibana monitors this index to display your audit trail.
def log_to_audit(action, message_id, status, details, **kwargs):
    """
    Creates a structured log via structlog and mirrors it to Elasticsearch.
    Kibana will easily parse the JSON fields.
    """
    # Create the structured log context
    log_entry = logger.bind(
        action=action,
        message_id=message_id,
        status=status,
        details=details,
        **kwargs
    )
    
    # Generate the log dict (this executes the processors, capturing trace_id)
    log_data = log_entry._context
    # Explicitly run processors to capture timestamp and trace_id for ES payload
    for proc in structlog.get_config()["processors"]:
        if proc != structlog.processors.JSONRenderer():
            log_data = proc(None, None, log_data)

    # Print JSON log to stdout
    log_entry.info("audit_event")

    # Index the same structured payload directly into Elasticsearch
    try:
        es_client.index(index=AUDIT_INDEX, document=log_data)
    except Exception as e:
        logger.error("elasticsearch_failed", error=str(e))

# 4. Kafka Producer Logic
def produce_message(topic, message_key, message_data):
    conf = {'bootstrap.servers': "localhost:9092"}
    producer = Producer(conf)
    
    with tracer.start_as_current_span("kafka_produce_operation") as span:
        payload = json.dumps(message_data).encode('utf-8')
        
        def delivery_report(err, msg):
            if err is not None:
                span.record_exception(err)
                span.set_status(trace.StatusCode.ERROR, str(err))
                log_to_audit("PRODUCE", message_key, "FAILED", str(err))
            else:
                log_to_audit(
                    "PRODUCE", 
                    message_key, 
                    "SUCCESS", 
                    "Message delivered to Kafka",
                    topic=msg.topic(),
                    partition=msg.partition()
                )

        producer.produce(topic, key=message_key, value=payload, callback=delivery_report)
        producer.flush()

# 5. Kafka Consumer Logic
def consume_messages(topic):
    conf = {
        'bootstrap.servers': "localhost:9092",
        'group.id': "audit-poc-group",
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([topic])

    logger.info("consumer_started", status="Listening for messages...", topic=topic)
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error("kafka_consumer_error", error=str(msg.error()))
                    break

            with tracer.start_as_current_span("kafka_consume_process") as span:
                key = msg.key().decode('utf-8') if msg.key() else "unknown"
                value = json.loads(msg.value().decode('utf-8'))
                
                # Business logic log
                log_to_audit(
                    "CONSUME", 
                    key, 
                    "SUCCESS", 
                    "Successfully processed payload",
                    payload=value
                )
                
    except KeyboardInterrupt:
        logger.info("consumer_shutdown", reason="KeyboardInterrupt")
    finally:
        consumer.close()

def run_poc():
    test_topic = "audit-poc-topic"
    produce_message(test_topic, "msg-101", {"user_id": "user_xyz", "amount": 999.00})
    consume_messages(test_topic)
    produce_message(test_topic, "msg-102", {"user_id": "user_xyz", "amount": 800.00})
    produce_message(test_topic, "msg-103", {"user_id": "user_xyz", "amount": 699.00})
    consume_messages(test_topic)
    consume_messages(test_topic)

if __name__ == "__main__":
    run_poc()
