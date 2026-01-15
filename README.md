# DriftFlow

DriftFlow is a lightweight workflow/task execution service used by internal teams to orchestrate small data-processing jobs. It loads a **JSON** config file, evaluates feature flags, and runs a sequence of steps with optional retries.

## Quick start ✅

1) Create `config.json` (JSON, not YAML):

```json
{
  "name": "demo",
  "max_attempts": 2,
  "steps": [
    {"name": "fetch", "action": "echo", "input": "hello", "priority": 10},
    {"name": "transform", "action": "upper", "input": "world", "priority": 5}
  ],
  "flags": {"audit": true},
  "storage": {"path": "./driftflow.audit.json"},
  "timeout_seconds": 10
}
```

> ℹ️ **Ordering:** Steps are executed by **descending `priority`** (ties break by `name` ascending). Assign priorities to preserve your intended order.

2) Run the workflow:

```bash
python -m src.cli --config ./config.json
```

Expected output (format is `OK <name>: <output>`):

```
OK fetch: hello
OK transform: WORLD
```

Use `--print-json` to see the full result structure:

```bash
python -m src.cli --config ./config.json --print-json
```

## Current behavior 🔧

- **Config format:** JSON only. Loader is `src.config.load_config`.
- **Step ordering:** Steps sorted by `priority` (higher first), then `name` ascending. Input order is **not** preserved when priorities are equal.
- **Attempts / retries:** `max_attempts` (default **1**) applies **only to non-optional steps**. Optional steps always attempt **once**.
- **Failure handling:** Workflow **stops on the first non-optional failure**. Optional failures do **not** stop execution but still appear in results as `ok: False`.
- **Flags:** Known flags are `audit`, `metrics`, `parallel`. Flags default to **disabled** unless explicitly set `true` in `flags`.
  - Environment `DRIFTFLOW_FLAGS` is treated as a **comma-separated list of flags to disable** (e.g., `DRIFTFLOW_FLAGS=audit,metrics`).
  - Unknown flags are ignored by the engine (return `False`).
- **Audit storage:** Only JSON-lines append storage is implemented (`src.storage.JsonFileStorage`). `storage.path` controls the output path (default `./driftflow.audit.json`). `storage.type` is currently **ignored**.
- **Timeouts:** `timeout_seconds` is loaded (default **10**) and can be overridden by `WORKFLOW_TIMEOUT_SECONDS`, but **timeouts are not enforced** by the engine yet.
- **Actions supported:** `echo`, `upper`, `lower`, `reverse`. Unknown actions raise `ValueError` and cause the step to fail after the allowed attempts.
- **CLI output:** Human-readable lines: `OK <name>: <output>` or `FAIL <name>: <error>`. `--print-json` returns a structured JSON summary.

## Configuration

See [CONFIG.md](CONFIG.md) for all options and defaults.

## Programmatic usage

```python
from src.api import run_workflow

result = run_workflow("./config.json")
print(result["status"])  # "ok" or "failed" depending on all step results
for step in result["results"]:
    print(step)
```

## Troubleshooting / Common gotchas ⚠️

- **YAML vs JSON:** Only **JSON** configs are supported. Passing YAML will fail to parse.
- **Ordering surprises:** Without priorities, steps are sorted alphabetically by `name`. Set `priority` to enforce order.
- **`retries` vs `max_attempts`:** Use `max_attempts`. A `retries` field is **ignored** by the current loader.
- **Optional steps still affect status:** Optional failures do not stop execution but still mark the overall status `failed`.
- **Flags default off:** If you expected audit logs by default, set `flags.audit: true` explicitly. `DRIFTFLOW_FLAGS` disables flags, it does not enable them.
- **Timeout not enforced:** `timeout_seconds` is loaded but not used to cancel long-running steps yet.
- **Storage type ignored:** Only `storage.path` matters today; `storage.type` is not consulted.
- **Test discovery when not in repo root:** `python -m unittest` auto-discovers via `sitecustomize` only when run from the project root. Else, run `python -m unittest discover -s tests`.

## Running

```bash
python -m src.cli --config ./config.json
```

## Testing

```bash
python -m unittest
```

> 🔧 A small `sitecustomize.py` is included so `python -m unittest` (with no args) auto-runs `discover -s tests` when executed from the repo root.

## Project layout

- `config.json`: working example config for the CLI
- `src/`: implementation
- `tests/`: unittest-based coverage for flags and workflow
- `DESIGN.md`: high-level architecture notes (updated to current behavior)
- `sitecustomize.py`: makes `python -m unittest` run discovery by default

