import json

from kafka import KafkaProducer
from shared.redis_state.redis_fraud_state import RedisState
from shared.events.fraud_alert import (
    create_fraud_alert
)

from shared.events.audit_event import (
    create_fraud_audit_event
)

from shared.errors.exceptions import (
    TransientProcessingError
)

from shared.logging_config import configure_logging

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    FRAUD_ALERTS_TOPIC,
    PAYMENT_AUDIT_TOPIC,
    LLM_REVIEW_TOPIC
)

from llm_router import should_route_to_llm

import logging 

configure_logging("fraud-service")
logger = logging.getLogger("fraud")

class FraudService:

    def __init__(self, rule_manager):

        self.producer = KafkaProducer(

            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),

            key_serializer=lambda key:
                key.encode("utf-8"),

            acks="all",
        )
        self.rule_manager = rule_manager

    def process(self, payment: dict):

        payment_id = payment.get("transaction_id")
        
                       
        logger.info(f"[FRAUD] Checking "
                    f"{payment['transaction_id']}",
                               extra={
                                   "event": "fraud_checking",
                                   "payment_id": payment_id
                               },
                              )
        
        
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

        routing = should_route_to_llm(
                    risk_score=risk_score,
                    triggered_rules=triggered_rules )
        
        if routing.required:

            llm_routing_result = {
                    "transaction_id": payment["transaction_id"],
                    "risk_score": risk_score,
                    "triggered_rules": triggered_rules,
                    "llm_review_required": routing.required,
                    "llm_routing_reason": routing.reason,
                    "customer_id": payment["customer_id"],
                    "amount": float(payment["amount"])
            }

            self.producer.send(
                    LLM_REVIEW_TOPIC,
    
                    key=payment["transaction_id"],
    
                    value=llm_routing_result,
                )

        if fraud:

            logger.info( f"[FRAUD] Detected "
                               f"transaction={payment['transaction_id']} "
                               f"risk_score={risk_score} "
                               f"rules={triggered_rules}",
                                           extra={
                                               "event": "fraud_detected",
                                               "payment_id": payment_id
                                           },
                                          )
            
            alert = create_fraud_alert(
                payment,
                rule_results,
            )

            self.producer.send(
                FRAUD_ALERTS_TOPIC,

                key=payment["customer_id"],

                value=alert,
            )

            audit = create_fraud_audit_event(

                event_type="PAYMENT_FRAUD_AUDIT",

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
                PAYMENT_AUDIT_TOPIC,
                key=json.dumps(payment["customer_id"]),
                value=audit)

            self.producer.flush()