# TaskLite Project Specification

## Purpose
Local task queue and scheduled execution tool for small Python services and workflows.

## Core Architecture
- **SQLite persistence**
- **Pre-registered local handlers**
- **Atomic job claim with leases**
- **State machine**: queued, running, succeeded, failed, cancelled
- **Exponential backoff retries**
- **Priority ordering**: high=10 > normal=5 > low=1
- **ISO-8601 UTC timezone-aware scheduling**
- **Status inspection**

## Security Boundary
- Pre-registered mock handlers only
- NO arbitrary shell execution
- NO pickle serialization (JSON payloads only)
- NO external network calls

## CLI commands
- `tasklite enqueue HANDLER --payload JSON_OR_FILE [--priority high/normal/low] [--queue QUEUE_NAME]`
- `tasklite worker [--queue QUEUE_NAME] [--burst] [--poll-interval SECONDS]`
- `tasklite status JOB_ID`
- `tasklite retry JOB_ID`
- `tasklite schedule HANDLER --at ISO8601_TIMESTAMP [--payload JSON_OR_FILE] [--queue QUEUE_NAME]`
- `tasklite list [--status STATUS] [--queue QUEUE_NAME] [--limit N]`
- `tasklite cancel JOB_ID`

## Exit codes
- `0`: Success
- `1`: Operation/validation failure
- `2`: CLI/input error
- `3`: Database/storage error

## Non-goals
Not a replacement for distributed brokers (Celery, RabbitMQ); local single-node / embedded use only.
