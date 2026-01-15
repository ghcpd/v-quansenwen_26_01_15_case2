# DriftFlow Configuration

This document describes the supported configuration options consumed by the JSON loader in [src/config.py](src/config.py).

## Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | "workflow" | Workflow name. |
| `steps` | list | required | Steps to execute (see below). |
| `flags` | map | `{}` | Feature flags. Recognized: `audit`, `metrics`, `parallel`. All default to **disabled**. |
| `storage` | map | `{ "path": "./driftflow.audit.json" }` | Audit storage settings. Uses an append-only JSON lines file. |
| `max_attempts` | int | 1 | Attempts for **non-optional** steps. Optional steps always run once. |
| `timeout_seconds` | int | 10 | Per-step timeout value stored in config (not currently enforced). |

`retries` is not consumed by the loader; use `max_attempts` instead.

## Steps

Each step accepts:

- `name` (string)
- `action` (string): one of `echo`, `upper`, `lower`, `reverse`
- `input` (string)
- `optional` (bool, default `false`)
- `priority` (int, default `0`)

Steps are sorted by `priority` descending and then by `name` alphabetically. A failed **non-optional** step stops the workflow. Failed optional steps do not stop later steps.

## Storage

```json
"storage": {
  "path": "./driftflow.audit.json"
}
```

The path is created if missing. One JSON object is appended per line when `audit` is enabled.

## Environment overrides

- `WORKFLOW_TIMEOUT_SECONDS` overrides `timeout_seconds` if it contains an integer.
- `DRIFTFLOW_FLAGS` accepts a comma-separated list of flags to **disable** (e.g., `DRIFTFLOW_FLAGS=audit,metrics`).
