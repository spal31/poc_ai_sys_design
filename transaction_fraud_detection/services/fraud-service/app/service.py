import json

from kafka import KafkaProducer
from redis_state import RedisState
from shared.events.fraud_alert import (
    create_fraud_alert
)

from shared.events.audit_event import (
    create_audit_event
)

from errors.exceptions import (
    TransientProcessingError
)

from validation import Validation

from shared.logging_config import configure_logging

import logging 
configure_logging("fraud-service")
logger = logging.getLogger("fraud")


FRAUD_TOPIC = "fraud-alerts"

AUDIT_TOPIC = "payment-audit"


class FraudService:

    def __init__(self, rule_manager):

        self.producer = KafkaProducer(

            bootstrap_servers="localhost:9092",

            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),

            key_serializer=lambda key:
                key.encode("utf-8"),

            acks="all",
        )
        self.rule_manager = rule_manager

    def process(self, payment: dict):

        payment_id = payment.get("payment_id")
        correlation_id = payment.get("correlation_id")
        
                       
        logger.info(f"[FRAUD] Checking "
                    f"{payment['transaction_id']}",
                               extra={
                                   "event": "fraud_checking",
                                   "payment_id": payment_id,
                                   "correlation_id": correlation_id,
                               },
                              )
        
        validation = Validation()
        validation.validate(payment)
        
        try:
          rule_results = self.rule_manager.evaluate(
                        payment
                    )
        
        except TimeoutError as exc:
        
          raise TransientProcessingError(
                        "Rule evaluation timed out"
                    ) from exc
        
        except ConnectionError as exc:
        
          raise TransientProcessingError(
                        "Temporary dependency failure"
                    ) from exc
        fraud = self.rule_manager.is_fraudulent(rule_results)
        
        redis_state = RedisState()
        redis_state.record_transaction(
        payment["customer_id"],
        payment["transaction_id"]
        )

        redis_state.add_customer_country(
        payment["customer_id"],
        payment["country"]
        )

        risk_score = sum(
            rule.score
            for rule in rule_results
            if rule.triggered
        )

        triggered_rules = [
            rule.rule_name
            for rule in rule_results
            if rule.triggered
        ]

        if fraud:

            logger.info( f"[FRAUD] "
                               f"transaction={payment['transaction_id']} "
                               f"risk_score={risk_score} "
                               f"rules={triggered_rules}",
                                           extra={
                                               "event": "fraud_detected",
                                               "payment_id": payment_id,
                                               "correlation_id": correlation_id,
                                           },
                                          )
            
            alert = create_fraud_alert(
                payment,
                rule_results,
            )

            self.producer.send(
                FRAUD_TOPIC,

                key=payment["customer_id"],

                value=alert,
            )

        audit = create_audit_event(

            event_type="FRAUD_CHECK",

            payment=payment,

            details={
                "risk_score": risk_score,

                "fraud": fraud,

                "rules_triggered":
                    triggered_rules,

                "service":
                    "fraud-service",
            },
        )

        self.producer.send(
            AUDIT_TOPIC,

            key=payment["customer_id"],

            value=audit,
        )

        self.producer.flush()