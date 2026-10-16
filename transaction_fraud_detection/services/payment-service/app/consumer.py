import json

from kafka import KafkaConsumer

from service import PaymentService

from shared.logging_config import configure_logging

from payment_dlq import DLQProducer

from shared.errors.retry import execute_with_retry

import logging 
configure_logging("payment-service")
logger = logging.getLogger("payment")

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_EVENTS_TOPIC,
    PAYMENT_CONSUMER_GROUP
)

from shared.errors.exceptions import (
    PermanentProcessingError,
    TransientProcessingError
)


class PaymentConsumer:

    def __init__(self):

        self.consumer = KafkaConsumer(
          PAYMENT_EVENTS_TOPIC,
          bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
          group_id=PAYMENT_CONSUMER_GROUP,
          auto_offset_reset="earliest",
          enable_auto_commit=False,
          value_deserializer=lambda value: json.loads(value.decode("utf-8")),
         )

        self.payment_service = PaymentService()
        self.dlq_producer = DLQProducer()

    def run(self):
        logger.info("Payment consumer started !!")

        while True:
            # kafka-python poll() returns a dict: {TopicPartition: [ConsumerRecord, ...]}
            # timeout_ms is used instead of seconds
            records_dict = self.consumer.poll(timeout_ms=1000)

            if not records_dict:
                continue

            # Iterate through the partitions and records
            for topic_partition, records in records_dict.items():

                for message in records:

                    retry_count = 0
                    try:
                        payment = message.value
                        payment_id = payment.get("transaction_id")
               
                        logger.info(f"PAYMENT CONSUMED"
                                   f"partition={message.partition} "
                                   f"offset={message.offset}",
                                    extra={ 
                                        "event": "payment_message_consumed",
                                        "payment_id": payment_id})

                        result, retry_count = execute_with_retry(lambda: self.payment_service.process(payment))

                        logger.info(f"PAYMENT CONSUMED SUCCESSFULLY PROCESSED "
                                    f"partition={message.partition} "
                                    f"offset={message.offset}",
                                    extra={
                                        "event": "payment_message_processed",
                                        "payment_id": payment_id})

                        self.consumer.commit()

                    except PermanentProcessingError as exc:
                        logger.exception(f"Permanent error: {exc}",
                                        extra={ "event": "fraud_checking",
                                                "payment_id": payment_id,
                                                })
                        self.send_to_dlq(message, payment, exc, retry_count)
                        self.consumer.commit()
                    
                    except TransientProcessingError as exc:
                        logger.exception(f"Retries exhausted: {exc}",
                                                                extra={ "event": "fraud_checking",
                                                                        "payment_id": payment_id})
                        self.send_to_dlq(message, payment, exc, retry_count=retry_count)
                        self.consumer.commit()
                    
                    except json.JSONDecodeError as exc:
                        logger.exception(f"Invalid JSON: {exc}",
                                                                extra={ "event": "fraud_checking",
                                                                        "payment_id": payment_id})
                        self.send_to_dlq(message, {}, exc, retry_count=0)
                        self.consumer.commit()
                    
                    except Exception as exc:
                        logger.exception(f"Unexpected error: {exc}",
                                                                extra={ "event": "fraud_checking",
                                                                        "payment_id": payment_id})
                        self.send_to_dlq(message, payment, exc, retry_count=0)
                        self.consumer.commit()
    
    def send_to_dlq(
        self,
        msg,
        payment,
        error,
        retry_count
    ):

        self.dlq_producer.send(
            original_event=payment,
            error=error,
            source_topic=msg.topic,
            source_partition=msg.partition,
            source_offset=msg.offset,
            retry_count=retry_count
        )

    
