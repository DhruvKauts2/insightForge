# ADR-0004: PostgreSQL for Relational and Operational Data

**Date:** 2026-05-16  
**Status:** Accepted

## Context

InsightForge has a class of data that does not fit the Elasticsearch document model well: user accounts, alert rule definitions, triggered alert history, and system configuration. This data is low-volume but requires ACID guarantees (e.g., creating an alert rule and its initial state atomically), foreign key relationships (triggered alerts reference alert rules), and transactional updates (acknowledging an alert). It also needs to be joinable — for example, listing all triggered alerts alongside their parent rule metadata.

## Decision

Use PostgreSQL 16 (Alpine) as the relational store for operational data. SQLAlchemy 2.0 is used as the ORM for Python services. The schema covers four tables:

| Table | Purpose |
|---|---|
| `users` | User accounts, bcrypt-hashed passwords, admin flag |
| `alert_rules` | Alert rule definitions (threshold, service, condition) |
| `triggered_alerts` | Alert history with acknowledgment status |
| `system_config` | Key-value runtime configuration |

Initialization SQL is mounted via `postgres-init/` and runs on first container startup.

## Consequences

**Positive**
- Full ACID semantics ensure alert rule mutations and triggered alert records are consistent.
- Foreign keys enforce referential integrity between `triggered_alerts` and `alert_rules`.
- SQLAlchemy 2.0's async engine integrates cleanly with FastAPI's async request handling.
- PostgreSQL is a mature, well-understood operational database with extensive ecosystem tooling.

**Negative**
- Two storage backends (Elasticsearch + PostgreSQL) must both be healthy for the system to be fully operational; partial failures require careful error handling in the API.
- The current Docker Compose networking means PostgreSQL is only directly reachable from within the `insightforge-network`; external tooling must connect via a tunnel or exposed port.
- No connection pooling middleware (e.g., PgBouncer) is in place; under high API concurrency, connection exhaustion is a risk.
- Credentials (`logflow` / `logflow123`) are hard-coded in `.env`; these must be rotated and managed via secrets in any production deployment.
