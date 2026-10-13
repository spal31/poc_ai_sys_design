import json

from kafka import KafkaConsumer

from service import PaymentService

from shared.logging_config import configure_logging

import logging 
configure_logging("payment-service")
logger = logging.getLogger("payment")



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
        payment_id = payment.get("payment_id")
        correlation_id = payment.get("correlation_id")

               
        logger.info(f"[PAYMENT CONSUMER] "
                                   f"partition={message.partition} "
                                   f"offset={message.offset}",
                       extra={
                           "event": "payment_message_consumed",
                           "payment_id": payment_id,
                           "correlation_id": correlation_id,
                       },
                      )

        payment_service.process(payment)

        # Commit only after successful processing.
        consumer.commit()

    except Exception as exc:

        print(
            f"Payment processing failed: {exc}"
        )

        logger.exception( f"Payment processing failed: {exc}",
                               extra={
                                   "event": "payment_message_consume_failed",
                                   "payment_id": payment_id,
                                   "correlation_id": correlation_id,
                               },
                              )