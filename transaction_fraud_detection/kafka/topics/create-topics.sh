#!/bin/bash

set -e

BOOTSTRAP_SERVER="localhost:9092"

echo "Waiting for Kafka to become available..."

until /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --list > /dev/null 2>&1
do
    echo "Kafka is not ready yet..."
    sleep 2
done

echo "Kafka is ready."

create_topic() {
    TOPIC=$1
    PARTITIONS=$2

    echo "Creating topic: $TOPIC"

    /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --create \
        --if-not-exists \
        --topic "$TOPIC" \
        --partitions "$PARTITIONS" \
        --replication-factor 1
}

create_topic "payment-events" 3
create_topic "payment-results" 3
create_topic "fraud-alerts" 3
create_topic "payment-audit" 3
create_topic "payment-dlq" 3
create_topic "llm-fraud-review" 3
create_topic "llm-fraud-decisions" 3


echo ""
echo "======================================"
echo "Kafka topics:"
echo "======================================"

/opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server "$BOOTSTRAP_SERVER" \
    --list

echo ""
echo "Kafka topic creation completed."