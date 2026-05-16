# ADR-0003: Elasticsearch as the Primary Log Storage Engine

**Date:** 2026-05-16  
**Status:** Accepted

## Context

Log data has properties that differ from typical business data: it is append-only, write-heavy, and read via full-text search and time-range aggregations rather than primary-key lookups. The query patterns include free-text search across `message` fields, filtering by `level` and `service`, time-series aggregations, and correlation ID lookups. A relational database can handle these queries but at the cost of complex indexing and poor full-text search ergonomics. A purpose-built columnar database (e.g., ClickHouse) would excel at aggregations but not at full-text search.

## Decision

Use Elasticsearch 8.11.1 as the primary store for all log documents. Log entries are indexed as JSON documents with fields `timestamp`, `level`, `service`, `message`, `correlation_id`, `request_id`, and `metadata`. Elasticsearch provides the following out of the box:

- Inverted index for `message` full-text search
- Term filters for `level` and `service`
- Date histogram aggregations for time-series charts
- BM25-ranked relevance scoring

PostgreSQL is used alongside Elasticsearch for structured relational data (users, alert rules, triggered alerts) where ACID guarantees and foreign key relationships matter.

## Consequences

**Positive**
- Full-text search on log messages is fast and ergonomic with Elasticsearch Query DSL.
- Date histogram aggregations for the dashboard metrics are handled natively.
- Schema flexibility: logs can carry arbitrary `metadata` without a migration.
- Horizontal scaling via sharding is built-in when volume grows.

**Negative**
- Elasticsearch is memory-hungry; the default JVM heap sizing needs tuning for the deployment environment.
- No ACID transactions — strong consistency within a document, but no cross-document atomicity.
- A separate PostgreSQL instance is still required for relational data, so two storage systems must be operated.
- Index management (ILM policies, shard allocation) adds operational overhead at scale.
- Elasticsearch license changed to SSPL in v7.11+; OSS alternatives (OpenSearch) should be evaluated for commercially sensitive deployments.
