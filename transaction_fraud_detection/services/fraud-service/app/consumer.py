import json

from kafka import KafkaConsumer

from shared.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    PAYMENT_EVENTS_TOPIC,
    FRAUD_CONSUMER_GROUP
)

from shared.errors.retry import execute_with_retry

from shared.logging_config import configure_logging

import logging 
configure_logging("fraud-service")
logger = logging.getLogger("fraud")

class FraudConsumer:

    def __init__(self, fraud_service):

        self.consumer = KafkaConsumer(
          PAYMENT_EVENTS_TOPIC,
          bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
          group_id=FRAUD_CONSUMER_GROUP,
          auto_offset_reset="earliest",
          enable_auto_commit=False,
          value_deserializer=lambda value: json.loads(value.decode("utf-8")),
         )

        self.fraud_service = fraud_service

    def run(self):
        logger.info("Fraud consumer started !!")

        while True:
            
            records_dict = self.consumer.poll(timeout_ms=1000)

            if not records_dict:
                continue

            # Iterate through the partitions and records
            for topic_partition, records in records_dict.items():
                for msg in records:
                    
                    # Initialize payment as an empty dict to ensure it's in scope for exceptions
                    payment = {}

                    try:
                        
                        payment = msg.value
                        payment_id = payment.get("payment_id")
                        correlation_id = payment.get("correlation_id")
                        
                        logger.info(f"Processing transaction {payment.get('transaction_id')}",
                                                       extra={
                                                           "event": "fraud_checking",
                                                           "payment_id": payment_id,
                                                           "correlation_id": correlation_id,
                                                       },
                                                      )

                        result, retry_count = execute_with_retry(
                            lambda: self.fraud_service.process(payment)
                        )

                        print(f"Fraud processing successful: {result}")
                        logger.info(f"Fraud processing successful: {result}",
                                                extra={
                                                    "event": "fraud_checking",
                                                    "payment_id": payment_id,
                                                    "correlation_id": correlation_id,
                                                },
                                                )

                        # kafka-python commit is synchronous by default, no message/asynchronous arguments needed
                        self.consumer.commit()

                    except Exception as exc:
                        logger.exception(f"Unexpected error: {exc}",
                                                             extra={ "event": "fraud_checking",
                                                                      "payment_id": payment_id,
                                                                       "correlation_id": correlation_id,})
                        self.consumer.commit()

