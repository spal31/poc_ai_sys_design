import os


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))


KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

PAYMENT_EVENTS_TOPIC = os.getenv(
    "PAYMENT_EVENTS_TOPIC",
    "payment-events"
)

PAYMENT_AUDIT_TOPIC = os.getenv(
    "PAYMENT_AUDIT_TOPIC",
    "payment-audit"
)

PAYMENT_RESULTS_TOPIC = os.getenv(
    "PAYMENT_RESULTS_TOPIC",
    "payment-results"
)

PAYMENT_CONSUMER_GROUP = os.getenv(
    "PAYMENT_CONSUMER_GROUP",
    "cg-payment-service"
)

FRAUD_ALERTS_TOPIC = os.getenv(
    "FRAUD_ALERTS_TOPIC",
    "fraud-alerts"
)

PAYMENT_DLQ_TOPIC = os.getenv(
    "PAYMENT_DLQ_TOPIC",
    "payment-dlq"
)

FRAUD_CONSUMER_GROUP = os.getenv(
    "FRAUD_CONSUMER_GROUP",
    "cg-fraud-service"
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)