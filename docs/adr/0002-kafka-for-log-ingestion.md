# ADR-0002: Apache Kafka for Log Ingestion

**Date:** 2026-05-16  
**Status:** Accepted

## Context

Log producers (applications, services) emit events at uneven, bursty rates. The downstream consumer pipeline (Elasticsearch indexing, anomaly detection) has finite throughput. Without a durable buffer between producers and consumers, a traffic spike can cause data loss or force the API service to apply back-pressure directly to log producers, coupling unrelated systems. We also need at-least-once delivery guarantees and the ability to replay events for reprocessing.

## Decision

Use Apache Kafka (v7.5.0, managed via Confluent Docker images with Zookeeper) as the central message bus. Log producers publish to the `logs-raw` topic. The consumer service reads from that topic in the `logflow-consumer` consumer group, batches messages, and bulk-indexes them into Elasticsearch.

Key configuration choices:
- Consumer batch size: 100 documents before flush
- Flush interval: 5 seconds (whichever triggers first)
- Consumer group enables horizontal scaling of consumer instances

## Consequences

**Positive**
- Producers are fully decoupled from consumers — a slow Elasticsearch cluster only builds backlog, it does not block log producers.
- Log events are durable on disk until consumed; replaying the topic recovers from a consumer outage.
- Multiple independent consumer groups can read the same topic (e.g., a future archival consumer alongside the indexer).
- Horizontal scaling of consumers is a configuration change, not a code change.

**Negative**
- Kafka + Zookeeper adds two more containers and significantly raises minimum infrastructure requirements.
- At-least-once delivery means the consumer must be idempotent; duplicate document IDs in Elasticsearch handle this but require stable ID generation.
- Operational expertise needed: partition count, retention policy, and consumer lag monitoring are non-trivial.
- Zookeeper dependency (not yet migrated to KRaft mode) is an additional failure point.
