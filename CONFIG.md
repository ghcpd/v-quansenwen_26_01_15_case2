# DriftFlow Configuration

This document describes the supported configuration options.

## Format

Configuration files must be in **JSON format**.

## Top-level fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | string | "workflow" | Workflow name. |
| `steps` | list | `[]` | Ordered list of steps to execute. |
| `max_attempts` | int | 1 | Number of attempts for each non-optional step. |
| `flags` | map | `{}` | Feature flags (default: all **disabled**). |
| `storage` | map | json config | Storage settings. |
| `timeout_seconds` | int | 10 | Per-step timeout (not currently enforced). |

## Steps

Each step requires:

- `name` (string): Step identifier
- `action` (string): one of `echo`, `upper`, `lower`, `reverse`
- `input` (string): Input value for the action
- `optional` (bool, default false): If true, failure does not stop workflow and step gets only 1 attempt
- `priority` (int, default 0): Higher priority steps run first; ties broken alphabetically by name

Steps execute in **priority order** (highest first), then alphabetically by name. A failed non-optional step stops the workflow.

## Feature Flags

All flags default to **disabled**. Explicitly enable them in your config:

```json
{
  "flags": {
    "audit": true,
    "metrics": false
  }
}
```

Known flags: `audit`, `metrics`, `parallel`. Unknown flags are always disabled.

## Storage

```json
{
  "storage": {
    "type": "json",
    "path": "./driftflow.audit.json"
  }
}
```

Currently only JSON append-only file storage is implemented. The `type` field is ignored.

## Environment overrides

- `WORKFLOW_TIMEOUT_SECONDS` overrides `timeout_seconds`.
- `DRIFTFLOW_FLAGS` accepts a comma-separated list of flags to **disable** (sets them to `false`).
