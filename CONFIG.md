# DriftFlow Configuration

This document describes the supported configuration options.

## Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | "workflow" | Workflow name. |
| `steps` | list | required | Ordered list of steps to execute. |
| `retries` | int | 3 | Number of retries for each step. |
| `flags` | map | `{}` | Feature flags (default: all enabled). |
| `storage` | map | sqlite config | Storage settings. |
| `timeoutSeconds` | int | 15 | Per-step timeout. |

## Steps

Each step requires:

- `name` (string)
- `action` (string): one of `echo`, `upper`, `lower`, `reverse`
- `input` (string)
- `optional` (bool, default false)

Steps execute in the exact order listed. If a step fails, it is logged and the workflow continues.

## Storage

```yaml
storage:
  type: sqlite
  path: "./driftflow.db"
```

## Environment overrides

- `DRIFTFLOW_TIMEOUT` overrides `timeoutSeconds`.
- `DRIFTFLOW_FLAGS` accepts a comma-separated list of enabled flags.
