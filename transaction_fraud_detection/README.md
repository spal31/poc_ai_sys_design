# Payment Fraud Detection POC

This repository contains a Proof of Concept (POC) for a **real-time payment fraud detection system**. The architecture leverages a distributed event-driven system with streaming pipelines, stateful redis lookup caches, asynchronous rule-based evaluation engines, and an LLM-powered reasoning layer for fraud analysis.

## 🏗️ Architecture & Component Overview

*   **Kafka**: The central event backbone facilitating decoupled, real-time message streaming.
*   **Redis**: High-performance, low-latency in-memory cache for fast evaluation of user profiles and fraud limits.
*   **Kafka Connect**: Configured with an Elasticsearch Sink Connector to pipeline transaction events into an audit log index automatically.
*   **Elasticsearch & Kibana**: Search, analytical ledger storage, and custom visualization dashboards for monitoring transactional flow and anomalous patterns.
*   **Payment Producer**: Simulation worker generating synthetic transaction events into the intake messaging stream.
*   **Payment Service**: Core ingestion system handling preliminary validation logic and state updates.
*   **Deterministic Fraud Service**: Static rule engine executing structured validation scripts to immediately flag high-risk transfers based on deterministic patterns.
*   **LLM Fraud Service**: Advanced semantic intelligence agent leveraging Large Language Models (LLMs) to inspect context-heavy transactions, identifying nuanced adversarial methodologies.

---

## 🚀 Step-by-Step Deployment Guide

Follow these steps sequentially to configure the infrastructure, populate historical cache datasets, and spin up active microservices.

### 1. Orchestrate Containerized Infrastructure
Bring up the distributed environment in detached mode using Docker Compose:
```bash
docker compose up -d
```

Monitor infrastructure instantiation and running status:
```bash
# Verify container wellness states
docker compose ps

# Follow real-time broker logs
docker compose logs -f kafka
```

Ensure the Kafka broker api-version is reachable over your local network interface:
```bash
docker compose exec kafka //opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

Proactively map dependencies by instantiating the required event brokers:
```bash
# Provision default message topics via bundled initialization automation script
docker compose exec kafka //opt/kafka/scripts/topics/create-topics.sh

# Confirm broker topics exist
docker compose exec kafka //opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Deep dive configuration details on partitions and replication factors
docker compose exec kafka //opt/kafka/bin/kafka-topics.sh --describe --topic payment-events --bootstrap-server localhost:9092
```

---

### 2. Verify Redis State Cache
Ensure the volatile key-value registry is running and accepting commands:
```bash
docker exec -it fraud-redis redis-cli
```
Inside the interactive prompt execution shell, run the following checks:
```redis
PING
INFO server
exit
```

---

### 3. Initialize Kafka Connect & Index Pipelines
Verify the state of the Kafka Connect engine endpoint:
```bash
curl http://localhost:8083/
```
Verify the availability of target plugins on your connect server path:
```bash
curl http://localhost:8083/connector-plugins
```

Submit structural deployment maps for your pipeline listeners:
```bash
# Instatiate Elasticsearch Sink connector bindings
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  --data @kafka-connect/connectors/elasticsearch-sink.json

# Establish transactional mapping structures for the Elasticsearch ingest framework
curl -X PUT http://localhost:9200/_index_template/payment-audit-template \
  -H "Content-Type: application/json" \
  --data @kafka-connect/elasticsearch-template.json
```

---

### 4. Health Check Analytics & UI Instances
Ensure search index managers and visual interfaces are operational:
```bash
# Verify Elasticsearch Core API is live
curl http://localhost:9200/
```
*   **Kibana Web Interface**: View transaction monitoring dashboards directly by navigating your web browser to `http://localhost:5601`.

---

### 5. Seed Historical Data & Run Services
Navigate to the root module layer containing core service engines:
```bash
cd services/
```

Execute each application instance below sequentially. Ensure paths are correctly configured by using explicit runtime environments via your workspace shell.

#### Step A: Seed the Redis Memory Layer
Populate mock customer profile configurations and structural balance sheets within the evaluation lookup store:
```bash
PYTHONPATH=. python shared/redis_state/seed_redis.py
```

#### Step B: Core Processing Node
Boot the transactional engine receiver:
```bash
PYTHONPATH=. python payment-service/app/main.py
```

#### Step C: Deterministic Fraud Engine
Boot the rule evaluation thread (optimized for static limits, velocity windows, and blacklist parameters):
```bash
# Set runtime workspace configurations
export PYTHONPATH=".;deterministic-fraud-service"
python deterministic-fraud-service/app/main.py
```

#### Step D: LLM Reasoning Service
Initialize the semantic analyzer node to address abstract fraud trends using natural language processors:
```bash
PYTHONPATH=. python llm-fraud-service/app/main.py
```

#### Step E: Payment Event Generator
Run the traffic driver worker to dispatch fake, randomly interleaved transaction sequences across the system pipeline:
```bash
PYTHONPATH=. python payment-producer/app/producer.py
```

---

## 📊 Monitoring Audit Logs

Confirm data is properly transferring across your active telemetry sinks to ensure end-to-end integration:

1. **Verify Elasticsearch Log Storage Status**:
   Inspect row-counts generated by target indices via the cluster catalog endpoints:
   ```bash
   curl http://localhost:9200/_cat/indices?v&s=docs.count:desc
   ```
   *Look for the `payment-audit` line item to verify document generation metrics increase actively over time.*

2. **Visual Inspection**:
   * Open `http://localhost:5601` in your browser.
   * Expand the menu drawer and select **Discover**.
   * Map your query patterns to view transaction timelines, evaluation outcomes, and flagged payment events in real time.
