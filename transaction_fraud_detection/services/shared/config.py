import os

# REDIS Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# KAFKA Server Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

# Payment Service Configuration
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

PAYMENT_DLQ_TOPIC = os.getenv(
    "PAYMENT_DLQ_TOPIC",
    "payment-dlq"
)

# Fraud Service Configuration
FRAUD_ALERTS_TOPIC = os.getenv(
    "FRAUD_ALERTS_TOPIC",
    "fraud-alerts"
)

FRAUD_CONSUMER_GROUP = os.getenv(
    "FRAUD_CONSUMER_GROUP",
    "cg-fraud-service"
)

# LLM Service Configuration
LLM_REVIEW_TOPIC = os.getenv(
    "LLM_REVIEW_TOPIC",
    "llm-fraud-review"
)

LLM_DECISION_TOPIC = os.getenv(
    "LLM_DECISION_TOPIC",
    "llm-fraud-decisions"
)

LLM_CONSUMER_GROUP = os.getenv(
    "LLM_CONSUMER_GROUP",
    "cg-llm-fraud-service"
)

MAX_AGENT_STEPS = os.getenv(
    "MAX_AGENT_STEPS",
    "8"
)

MAX_LLM_RETRIES = os.getenv(
    "MAX_LLM_RETRIES",
    "1"
)

# Langfuse Observability Configuration
LANGFUSE_PUBLIC_KEY = os.getenv(
    "LANGFUSE_PUBLIC_KEY",
    ""
)

LANGFUSE_SECRET_KEY = os.getenv(
    "LANGFUSE_SECRET_KEY",
    ""
)

LANGFUSE_BASE_URL = os.getenv(
    "LANGFUSE_BASE_URL",
    ""
)

LANGFUSE_TRACING_ENVIRONMENT = os.getenv(
    "LANGFUSE_TRACING_ENVIRONMENT",
    ""
)

LANGFUSE_TRACING_ENVIRONMENT = os.getenv(
    "LANGFUSE_TRACING_ENVIRONMENT",
    ""
)

# OPENAI Configuration
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    ""
)

MAX_RETRIES = int(
    os.getenv("MAX_RETRIES", "3")
)