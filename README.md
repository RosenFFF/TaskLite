# TaskLite

> **Note**: This repository is a synthetic benchmark created for evaluating RepoCare.
> Its issues and pull requests are intentionally designed test cases.
> They do not represent real community reports or external maintainer adoption.

## Features
- Local task queue and scheduled execution.
- Backed by SQLite for easy persistence.
- JSON payloads, pre-registered local handlers.

## Installation
```bash
pip install -e .
```

## Quick Start
```bash
# Enqueue a task
tasklite enqueue my_handler --payload '{"data": "example"}'

# Start a worker
tasklite worker
```

## CLI Command Reference
- `tasklite enqueue ...`
- `tasklite worker ...`
- `tasklite status ...`
- `tasklite retry ...`
- `tasklite schedule ...`
- `tasklite list ...`
- `tasklite cancel ...`

## Security & Constraints
- No network access during execution.
- Local JSON payload only.
- Pre-registered handlers only.

## License
MIT
