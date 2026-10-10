# Architecture

## SQLite lock/lease mechanism
Workers claim jobs by atomic UPDATE statements with `UPDATE ... SET status='running', lease_timeout=... WHERE status='queued' AND ...`.

## State machine transitions
- `queued` -> `running`
- `running` -> `succeeded`
- `running` -> `failed`
- `queued` | `running` -> `cancelled`

## Retry backoff calculation
Retries use an exponential backoff formula based on attempt count.
