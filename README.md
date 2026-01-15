# DriftFlow

DriftFlow is a lightweight workflow/task execution service used by internal teams to orchestrate small data-processing jobs. It loads a JSON config file, evaluates feature flags, and runs a sequence of steps with retries.

## Quick start

1. Create a config file (JSON):

```json
{
  "name": "demo",
  "steps": [
    {"name": "fetch", "action": "echo", "input": "hello", "priority": 1},
    {"name": "transform", "action": "upper", "input": "world", "priority": 0}
  ],
  "flags": {
    "audit": true,
    "metrics": true
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

- Steps are sorted by **priority** (descending), then by **name** (ascending).
- Retries are configured via `max_attempts` (default: 1, meaning no retries).
- Feature flags are **disabled by default** and must be explicitly enabled in the config.
- `audit` logging is off by default; set `"audit": true` in `flags` to enable it.
- Storage uses a JSON file backend (append-only) and writes to `./driftflow.audit.json` by default.
- Failed steps that are **not optional** will **stop** the workflow. Optional steps never stop the workflow.
- `WORKFLOW_TIMEOUT_SECONDS` environment variable controls the per-step timeout in seconds (default: 10).

## Configuration

See [CONFIG.md](CONFIG.md) for all options.

## Programmatic usage

```python
from src.api import run_workflow

result = run_workflow("./config.json")
print(result["status"])  # "ok" or "failed"
```

## Running tests

```bash
python -m unittest discover -s tests
```

## Project layout

- src/: implementation
- tests/: unit tests (uses stdlib `unittest`)
- DESIGN.md: high-level architecture notes

## Troubleshooting / Common gotchas

1. **Config must be JSON** — YAML is not supported. The config loader uses `json.load()`.

2. **Flags are disabled by default** — Unlike some documentation may suggest, flags like `audit` and `metrics` default to `false`. You must explicitly set them to `true` in your config.

3. **Steps are sorted, not FIFO** — Steps are sorted by `priority` (high to low), then alphabetically by `name`. If you want FIFO order, give all steps the same priority (or omit `priority`).

4. **Non-optional failures stop the workflow** — If a step fails and `optional` is not `true`, the workflow halts. Use `"optional": true` for steps that should not block execution.

5. **`retries` vs `max_attempts`** — The config field is `max_attempts`, not `retries`. A value of `1` means one attempt with no retries. Note: optional steps always run exactly once (no retries).

6. **Environment variable names** — Use `WORKFLOW_TIMEOUT_SECONDS` (not `DRIFTFLOW_TIMEOUT`). Use `DRIFTFLOW_FLAGS` to disable flags (comma-separated list of flag names to set to `false`).
