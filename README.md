# DriftFlow

DriftFlow is a lightweight workflow/task execution service used by internal teams to orchestrate small data-processing jobs. It loads a config file, evaluates feature flags, and runs a sequence of steps with retries.

## Quick start

1. Create a config file (YAML):

```yaml
name: "demo"
steps:
  - name: "fetch"
    action: "echo"
    input: "hello"
  - name: "transform"
    action: "upper"
    input: "world"
flags:
  audit: true
  metrics: true
storage:
  type: sqlite
  path: "./driftflow.db"
retries: 3
```

2. Run the workflow:

```bash
python -m src.cli --config ./config.yml
```

Expected output:

```
OK fetch => hello
OK transform => WORLD
```

## Behavior

- Steps execute in **FIFO** order as they appear in the config.
- Retries are enabled by default and can be configured via `retries` (default: 3).
- Feature flags are **enabled by default** and can be overridden in the config.
- `audit` logging is on by default and writes to the configured storage backend.
- Storage uses SQLite by default and will create the database file if missing.
- Failed steps are logged and **do not stop** the workflow.
- `DRIFTFLOW_TIMEOUT` controls the per-step timeout in seconds.

## Configuration

See [CONFIG.md](CONFIG.md) for all options.

## Programmatic usage

```python
from src.api import run_workflow

result = run_workflow("./config.yml")
print(result["status"])  # "ok"
```

## Project layout

- src/: implementation
- tests/: (some coverage; may be outdated)
- DESIGN.md: high-level architecture notes
