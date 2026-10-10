# Changelog

## [0.1.1] - 2026-10-10
### Added
- Queue inspection `tasklite stats` command with status aggregations.
- Filtering by queue, status, and custom limit in `tasklite list`.

## [0.1.0] - 2026-10-10
### Added
- SQLite persistence with atomic job claim and lease expiration recovery.
- Priority scheduling (high > normal > low) and FIFO ordering.
- Exponential backoff retry policy adhering to `1 + max_retries` attempts.
- Timezone-aware ISO-8601 scheduling.
- Worker execution with timeout handling and burst execution mode.
- Click CLI interface with full command suite.
