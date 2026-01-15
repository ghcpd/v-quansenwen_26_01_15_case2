# DriftFlow

DriftFlow is a lightweight workflow/task execution service used by internal teams to orchestrate small data-processing jobs. It loads a config file, evaluates feature flags, and runs a sequence of steps with retries.

## Quick start

1. Create a config file (JSON):

```json
{
  "name": "demo",
  "steps": [
    {"name": "fetch", "action": "echo", "input": "hello"},
    {"name": "transform", "action": "upper", "input": "world"}
  ],
  "flags": {
    "audit": true
  },
  "storage": {
    "type": "json",
    "path": "./driftflow.audit.json"
  },
  "max_attempts": 3
}
```

2. Run the workflow:

```bash
python -m src.cli --config ./config.json
```

Expected output:

```
OK fetch: hello
OK transform: WORLD
```

## Behavior

- Steps execute in **priority order** (highest `priority` first), then **alphabetically by name**. Steps without a priority field default to priority 0.
- Retries can be configured via `max_attempts` (default: 1). Optional steps always get 1 attempt regardless of this setting.
- Feature flags are **disabled by default** and must be explicitly enabled in the config.
- `audit` logging is off by default; enable it with `"flags": {"audit": true}` to write events to the storage backend.
- Storage uses JSON append-only file by default (`./driftflow.audit.json`).
- Failed **non-optional** steps **stop** the workflow; failed **optional** steps are logged but do not stop execution.
- `WORKFLOW_TIMEOUT_SECONDS` environment variable overrides the `timeout_seconds` config value.

## Configuration

See [CONFIG.md](CONFIG.md) for all options.

## Programmatic usage

```python
from src.api import run_workflow

result = run_workflow("./config.json")
print(result["status"])  # "ok" or "failed"
print(result["results"])  # list of step results
```

## Troubleshooting / Common gotchas

1. **Config file format**: Must be JSON, not YAML. Use `.json` extension and JSON syntax.
2. **Feature flags default to OFF**: To enable audit logging, explicitly set `"flags": {"audit": true}` in your config.
3. **Execution order**: Steps run by priority (highest first), then alphabetically. If you need specific order, use the `priority` field or name steps accordingly (e.g., `step_01`, `step_02`).
4. **Failures stop execution**: A failed non-optional step stops the workflow. Mark steps as `"optional": true` if you want the workflow to continue on failure.
5. **Field name is `max_attempts`, not `retries`**: Use `"max_attempts": 3` in your config.
6. **Environment variable**: Use `WORKFLOW_TIMEOUT_SECONDS`, not `DRIFTFLOW_TIMEOUT`.
7. **Storage backend**: Only JSON file storage is implemented. The `type` field is ignored; it always uses JSON append-only log.

## Project layout

- src/: implementation
- tests/: test suite (run with `python -m unittest`)
- DESIGN.md: high-level architecture notes
