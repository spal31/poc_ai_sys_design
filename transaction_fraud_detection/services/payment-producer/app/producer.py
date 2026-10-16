import json
import random
import time
import uuid

from datetime import datetime, timezone
from decimal import Decimal

from kafka import KafkaProducer

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_EVENTS_TOPIC
)


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

    value_serializer=lambda value:
        json.dumps(value).encode("utf-8"),

    key_serializer=lambda key:
        key.encode("utf-8") if key else None,

    acks="all",

    retries=5,

    linger_ms=5,

    batch_size=16384,
)


def generate_payment_event() -> dict:

    transaction_id = str(uuid.uuid4())

    customer_id = f"customer-{random.randint(1, 10)}"

    event = {
        "event_id": str(uuid.uuid4()),

        "transaction_id": transaction_id,

        "customer_id": customer_id,

        "amount": str(
            Decimal(
                random.randint(-500, 2000)
            )
        ),

        "currency": "INR",

        "merchant_id":
            f"merchant-{random.randint(1, 5)}",

        "payment_method":
            random.choice([
                "CARD",
                "UPI",
                "NET_BANKING",
            ]),

        "country":
            random.choice([
                "IN",
                "US",
                "GB",
                "CA"
            ]),

        "ip_address":
            f"192.168.1.{random.randint(1, 254)}",

        "device_id":
            f"device-{random.randint(1, 20)}",

        "timestamp":
            datetime.now(timezone.utc).isoformat(),

        "status": "INITIATED",
    }

    return event


def send_payment():

    event = generate_payment_event()

    customer_id = event["customer_id"]
    transaction_id = event["transaction_id"]

    future = producer.send(
        PAYMENT_EVENTS_TOPIC,

        key=customer_id,

        value=event,
    )

    metadata = future.get(timeout=10)

    print(
        f"Published transaction={transaction_id} for customer={customer_id}"
        f"partition={metadata.partition} "
        f"offset={metadata.offset}"
    )


if __name__ == "__main__":

    try:

        while True:

            send_payment()

            time.sleep(10)

    except KeyboardInterrupt:

        print("Stopping producer...")

    finally:

        producer.flush()
        producer.close()