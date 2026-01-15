# DriftFlow Configuration

This document describes the configuration that the **current implementation** actually consumes (`src.config.load_config` + `src.workflow.WorkflowEngine`).

## Top-level fields

| Field             | Type   | Default                  | Description |
|------------------|--------|--------------------------|-------------|
| `name`           | string | `"workflow"`            | Workflow name. |
| `steps`          | list   | `[]`                     | Steps to execute (sorted by priority, not insertion order). |
| `max_attempts`   | int    | `1`                      | Attempts for **non-optional** steps. Optional steps always attempt once. |
| `flags`          | map    | `{}`                     | Feature flags (all **disabled** by default). Known: `audit`, `metrics`, `parallel`. |
| `storage`        | map    | `{ "path": "./driftflow.audit.json", "type": "json" }` | Storage settings; only `path` is used. |
| `timeout_seconds`| int    | `10`                     | Loaded from config/env but **not enforced** by the engine yet. |

> ⚠️ The field `retries` is **ignored** by the current loader. Use `max_attempts` instead.

## Steps

Each step may include:

- `name` (string, default `"step"`)
- `action` (string, **required**): one of `echo`, `upper`, `lower`, `reverse`
- `input` (string, default `""`)
- `optional` (bool, default `false`)
- `priority` (int, default `0`): higher runs earlier; ties break by `name` ascending.

Execution order is computed by sorting steps by `priority` descending, then `name` ascending. Input order is not preserved when priorities tie.

If a step fails:
- Non-optional: the workflow stops after the allowed attempts (`max_attempts`).
- Optional: the workflow continues, but the result for that step will still be `ok: False`.

## Storage

```json
"storage": {
  "path": "./driftflow.audit.json",
  "type": "json"  // currently ignored
}
```

Storage is append-only JSON-lines (`src.storage.JsonFileStorage`). A `ts` timestamp (seconds) is added when writing events.

## Environment overrides

- `WORKFLOW_TIMEOUT_SECONDS` → sets `timeout_seconds` (must be an int; otherwise ignored). **Note:** timeouts are not enforced yet.
- `DRIFTFLOW_FLAGS` → comma-separated list of flags to **disable** (e.g., `DRIFTFLOW_FLAGS=audit,metrics`). Unknown flags are ignored by the engine.

> 🔁 Merging behavior: config is shallow-merged over defaults. If you provide `storage`, include all needed keys (the default `type` won’t be merged into your custom map).
