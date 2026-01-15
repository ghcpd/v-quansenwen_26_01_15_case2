# DriftFlow

DriftFlow is a lightweight workflow/task execution service used to orchestrate small jobs. It loads a JSON config file, applies feature flags, and runs steps with simple auditing.

## Quick start

1) Create `config.json` in the repo root (see the checked-in example):

```json
{
  "name": "demo",
  "steps": [
    {"name": "fetch", "action": "echo", "input": "hello"},
    {"name": "transform", "action": "upper", "input": "world", "priority": 1}
  ],
  "flags": {"audit": true},
  "storage": {"path": "./driftflow.audit.json"},
  "max_attempts": 2,
  "timeout_seconds": 10
}
```

2) Run the workflow:

```bash
python -m src.cli --config ./config.json
```

Expected output:

```
OK transform: WORLD
OK fetch: hello
```

## Behavior

- Steps are ordered by `priority` (higher first) then by `name` alphabetically; not strictly FIFO.
- `max_attempts` controls retries for non-optional steps (default: 1); optional steps always run once.
- A non-optional failure stops the workflow; optional steps may fail without stopping.
- Feature flags default to disabled. Only `audit`, `metrics`, and `parallel` are recognized; unknown flags are treated as off.
- The `DRIFTFLOW_FLAGS` environment variable disables listed flags (e.g., `DRIFTFLOW_FLAGS=audit,metrics`).
- Audit writes append-only JSON lines to the configured path; storage uses a local file, not SQLite.
- `WORKFLOW_TIMEOUT_SECONDS` overrides `timeout_seconds` in the loaded config.
- `run_workflow()` returns `status: "ok"` only when all steps succeed.

## Configuration

See [CONFIG.md](CONFIG.md) for full options and environment overrides.

## Programmatic usage

```python
from src.api import run_workflow

result = run_workflow("./config.json")
print(result["status"])  # "ok" when all steps succeed
```

## Troubleshooting / Common gotchas

- Config must be JSON; YAML is not supported by the loader.
- Flags are off by default; set `"audit": true` to enable auditing.
- `DRIFTFLOW_FLAGS` only disables flags, even if the config enables them.
- Use `max_attempts`, not `retries`; missing or zero values mean one attempt.
- Non-optional failures stop later steps; make a step optional to continue after its failure.
- Step order changes with `priority`; equal priorities fall back to alphabetical `name` order.

## Project layout

- src/: implementation
- tests/: stdlib `unittest` coverage
- DESIGN.md: architecture notes
