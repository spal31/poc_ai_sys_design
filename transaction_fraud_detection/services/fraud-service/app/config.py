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

FRAUD_ALERTS_TOPIC = os.getenv(
    "FRAUD_ALERTS_TOPIC",
    "fraud-alerts"
)

FRAUD_DLQ_TOPIC = os.getenv(
    "FRAUD_DLQ_TOPIC",
    "fraud-dlq"
)

FRAUD_CONSUMER_GROUP = os.getenv(
    "FRAUD_CONSUMER_GROUP",
    "cg-fraud-service"
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)