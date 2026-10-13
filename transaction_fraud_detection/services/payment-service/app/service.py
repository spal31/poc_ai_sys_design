import json
import logging

from kafka import KafkaProducer

from shared.events.payment_result import (
    create_payment_result
)

from shared.events.audit_event import (
    create_audit_event
)


from shared.logging_config import configure_logging

configure_logging("payment-service")
logger = logging.getLogger("payment")


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

       payment_id = payment.get("payment_id")
       correlation_id = payment.get("correlation_id")
       
       logger.info(
               "Processing payment",
               extra={
                   "event": "payment_processing_started",
                   "payment_id": payment_id,
                   "correlation_id": correlation_id,
               },
              )
       
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