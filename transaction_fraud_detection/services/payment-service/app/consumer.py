import json

from kafka import KafkaConsumer

from service import PaymentService


TOPIC = "payment-events"

GROUP_ID = "cg-payment-service"


consumer = KafkaConsumer(

    TOPIC,

    bootstrap_servers="localhost:9092",

    group_id=GROUP_ID,

    auto_offset_reset="earliest",

    enable_auto_commit=False,

    value_deserializer=lambda value:
        json.loads(value.decode("utf-8")),
)


payment_service = PaymentService()


print(
    f"Payment Service started. "
    f"Consumer group={GROUP_ID}"
)


for message in consumer:

    try:

        payment = message.value

        print(
            f"[PAYMENT CONSUMER] "
            f"partition={message.partition} "
            f"offset={message.offset}"
        )

        payment_service.process(payment)

        # Commit only after successful processing.
        consumer.commit()

    except Exception as exc:

        print(
            f"Payment processing failed: {exc}"
        )

        # Do NOT commit.
        #
        # The message can be processed again.