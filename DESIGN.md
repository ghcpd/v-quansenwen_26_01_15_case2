# DriftFlow Design Notes (current implementation)

## Overview

DriftFlow is a minimal workflow engine used by multiple internal teams. The current codebase provides:

- Deterministic execution order via **priority sorting** (descending `priority`, then `name` ascending)
- Fixed-attempt retries via `max_attempts` (no exponential backoff implemented)
- A **JSON-lines file** audit sink (`src.storage.JsonFileStorage`)
- Audit logging **only when the `audit` flag is enabled**

## Execution model

- Steps are materialized into `Step` dataclasses (`name`, `action`, `input`, `optional`, `priority`).
- Execution order is derived from sorting, not insertion order.
- Non-optional steps are retried up to `max_attempts` (default 1). Optional steps are attempted once.
- On the first **non-optional** failure, the workflow stops. Optional failures do **not** stop execution but still contribute a failed result.
- Supported actions: `echo`, `upper`, `lower`, `reverse`. Unknown actions raise and are treated as failures.

### Timeouts

`timeout_seconds` is loaded (default 10; overridable via `WORKFLOW_TIMEOUT_SECONDS`) but is **not enforced** by the engine yet.

## Storage

- Only `JsonFileStorage` is implemented. It appends one JSON object per line and adds a `ts` timestamp when writing.
- `storage.path` controls the output path. `storage.type` is currently ignored.

## Feature flags

- Known flags: `audit`, `metrics`, `parallel` (`src.flags.KNOWN_FLAGS`).
- Flags are **opt-in** (default False). Unknown flags return False.
- `DRIFTFLOW_FLAGS` is interpreted as a **disable list** (flags listed are set False).

## Backward compatibility notes

- The legacy `retries` field is **not consumed**; use `max_attempts` instead.
- Only JSON configs are supported; YAML is not.

> 🛠️ Future work ideas: enforce timeouts, implement backoff, add storage abstraction for sqlite/memory, and reconsider optional-step contribution to overall status.