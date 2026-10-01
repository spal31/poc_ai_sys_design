import json

from kafka import KafkaProducer

from shared.events.payment_result import (
    create_payment_result
)

from shared.events.audit_event import (
    create_audit_event
)


RESULT_TOPIC = "payment-results"
AUDIT_TOPIC = "payment-audit"


class PaymentService:

    def __init__(self):

        self.producer = KafkaProducer(
            bootstrap_servers="localhost:9092",

            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),

            key_serializer=lambda key:
                key.encode("utf-8"),

            acks="all",
        )

    def process(self, payment: dict):

        print(
            f"[PAYMENT] Processing "
            f"{payment['transaction_id']}"
        )

        # POC business processing.
        #
        # Later this would call:
        # - payment gateway
        # - authorization service
        # - payment database
        # etc.

        result = create_payment_result(
            payment=payment,
            status="APPROVED",
        )

        self.producer.send(
            RESULT_TOPIC,
            key=payment["customer_id"],
            value=result,
        )

        audit = create_audit_event(
            event_type="PAYMENT_PROCESSED",

            payment=payment,

            details={
                "status": "APPROVED",
                "service": "payment-service",
            },
        )

        self.producer.send(
            AUDIT_TOPIC,
            key=payment["customer_id"],
            value=audit,
        )

        self.producer.flush()