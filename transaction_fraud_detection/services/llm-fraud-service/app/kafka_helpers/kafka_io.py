
import json

from kafka import KafkaConsumer, KafkaProducer

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    LLM_REVIEW_TOPIC,
    LLM_CONSUMER_GROUP
)



def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
          LLM_REVIEW_TOPIC,
          bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
          group_id=LLM_CONSUMER_GROUP,
          auto_offset_reset="earliest",
          enable_auto_commit=False,
          value_deserializer=lambda value: json.loads(value.decode("utf-8")),
         )


def create_producer() -> KafkaProducer:
    return KafkaProducer(

            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,

            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),

            key_serializer=lambda key:
                key.encode("utf-8"),

            acks="all",
        )


def publish_to_kafka(
    producer: KafkaProducer,
    topic: str,
    payload: dict,
) -> None:
    producer.send(
                topic,

                key=payload["transaction_id"],

                value=payload)

    producer.flush()
