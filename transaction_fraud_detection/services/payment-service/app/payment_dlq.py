import json
from datetime import datetime, timezone

from kafka import KafkaProducer

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_DLQ_TOPIC,
    PAYMENT_CONSUMER_GROUP
)


class DLQProducer:

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send(
        self,
        original_event: dict,
        error: Exception,
        source_topic: str,
        source_partition: int,
        source_offset: int,
        retry_count: int
    ):

        dlq_event = {
            "original_event": original_event,

            "error": {
                "error_type": type(error).__name__,
                "error_message": str(error),
                "retryable": False
            },

            "metadata": {
                "source_topic": source_topic,
                "source_partition": source_partition,
                "source_offset": source_offset,
                "consumer_group": PAYMENT_CONSUMER_GROUP,
                "retry_count": retry_count,
                "failed_at": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        }

        transaction_id = original_event.get(
            "transaction_id",
            "unknown"
        )

        self.producer.send(
            topic=PAYMENT_DLQ_TOPIC,
            key=transaction_id.encode('utf-8') if transaction_id else None, 
            value=dlq_event
        )

        self.producer.flush()