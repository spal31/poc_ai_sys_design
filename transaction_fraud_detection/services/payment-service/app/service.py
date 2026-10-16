import json
import logging

from kafka import KafkaProducer

from shared.events.payment_result import (
    create_payment_result
)

from shared.events.audit_event import (
    create_payment_audit_event
)


from shared.logging_config import configure_logging

configure_logging("payment-service")
logger = logging.getLogger("payment")

from validation import Validation

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_AUDIT_TOPIC,
    PAYMENT_RESULTS_TOPIC
)


class PaymentService:

    def __init__(self):

        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),

            key_serializer=lambda key:
                key.encode("utf-8"),

            acks="all",
        )

    def publish_payment_result(self, payment: dict, success: bool):
    
            result = create_payment_result(
                                payment=payment,
                                status="APPROVED" if success else "FAILED",
                            )
            
            self.producer.send(
                    PAYMENT_RESULTS_TOPIC,
                    key=payment["customer_id"],
                    value=result,
                )
    
            audit = create_payment_audit_event(
                    event_type="PAYMENT_PROCESSED",
    
                    payment=payment,
    
                    details={
                        "status": "APPROVED" if success else "FAILED",
                        "service": "payment-service",
                    },
                )
    
            self.producer.send(
                    PAYMENT_AUDIT_TOPIC,
                    key=json.dumps(payment["customer_id"]),
                    value=audit,
                )
    
            self.producer.flush()

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
       try: 
            validation = Validation()
            validation.validate(payment)
            
            self.publish_payment_result(payment, True)

       except Exception as exc:

            self.publish_payment_result(payment, False)

            raise