import json

from kafka import KafkaProducer

from shared.events.fraud_alert import (
    create_fraud_alert
)

from shared.events.audit_event import (
    create_audit_event
)


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

        print(
            f"[FRAUD] Checking "
            f"{payment['transaction_id']}"
        )

        rule_results = self.rule_manager.evaluate(payment)
        print("rule_results")
        print(rule_results[0])
        print(rule_results[1])
        fraud = self.rule_manager.is_fraudulent(rule_results)

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

        print(
            f"[FRAUD] "
            f"transaction={payment['transaction_id']} "
            f"risk_score={risk_score} "
            f"rules={triggered_rules}"
        )

        if fraud:

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