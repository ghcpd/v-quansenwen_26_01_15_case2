# DriftFlow Configuration

This document describes the supported configuration options.

## File format

Configuration files must be **JSON** (not YAML).

## Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | `"workflow"` | Workflow name. |
| `steps` | list | `[]` | Ordered list of steps to execute (sorted by priority then name). |
| `max_attempts` | int | `1` | Maximum attempts per non-optional step. |
| `flags` | map | `{}` | Feature flags (default: all **disabled**). |
| `storage` | map | see below | Storage settings. |
| `timeout_seconds` | int | `10` | Per-step timeout (not currently enforced in code). |

## Steps

Each step supports:

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | `"step"` | Step identifier (used in output and sorting). |
| `action` | string | `"echo"` | One of: `echo`, `upper`, `lower`, `reverse`. |
| `input` | string | `""` | Input string passed to the action. |
| `optional` | bool | `false` | If `true`, failure does not stop the workflow and no retries are attempted. |
| `priority` | int | `0` | Higher priority steps run first. Steps with equal priority are sorted by name (ascending). |

### Execution order

Steps are sorted by:
1. `priority` descending (higher values first)
2. `name` ascending (alphabetical)

This means the order in the config file does **not** determine execution order unless all priorities are equal.

### Failure behavior

- If a non-optional step fails after all retry attempts, the workflow **stops** (remaining steps are skipped).
- Optional steps run exactly once (no retries) and never stop the workflow.

## Feature flags

Known flags: `audit`, `metrics`, `parallel`.

- All flags are **disabled by default**.
- Set a flag to `true` in the config to enable it.

Example:
```json
"flags": {
  "audit": true,
  "metrics": false
}
```

When `audit` is enabled, the storage backend records each step execution.

## Storage

The storage backend persists audit events as newline-delimited JSON.

| Field | Type | Default | Description |
|---|---|---|---|
| `type` | string | `"json"` | Storage type (only `json` is implemented). |
| `path` | string | `"./driftflow.audit.json"` | Path to the audit log file. |

Example:
```json
"storage": {
  "type": "json",
  "path": "./driftflow.audit.json"
}
```

## Environment overrides

| Variable | Effect |
|---|---|
| `WORKFLOW_TIMEOUT_SECONDS` | Overrides `timeout_seconds` from config. |
| `DRIFTFLOW_FLAGS` | Comma-separated list of flag names to **disable** (set to `false`). |

Example:
```bash
export WORKFLOW_TIMEOUT_SECONDS=30
export DRIFTFLOW_FLAGS="audit,metrics"  # disables audit and metrics
```
