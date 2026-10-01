import json

from kafka import KafkaConsumer

from service import FraudService
from rules.rule_registry import create_rule_manager

TOPIC = "payment-events"

GROUP_ID = "cg-fraud-service"


consumer = KafkaConsumer(

    TOPIC,

    bootstrap_servers="localhost:9092",

    group_id=GROUP_ID,

    auto_offset_reset="earliest",

    enable_auto_commit=False,

    value_deserializer=lambda value:
        json.loads(value.decode("utf-8")),
)

rule_manager = create_rule_manager()

fraud_service = FraudService(rule_manager=rule_manager)


print(
    f"Fraud Service started. "
    f"Consumer group={GROUP_ID}"
)


for message in consumer:

    try:

        payment = message.value

        print(
            f"[FRAUD CONSUMER] "
            f"partition={message.partition} "
            f"offset={message.offset}"
        )

        fraud_service.process(payment)

        consumer.commit()

    except Exception as exc:

        print(
            f"Fraud processing failed: {exc}"
        )

        # Do not commit.