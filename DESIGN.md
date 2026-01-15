# DriftFlow Design Notes

## Overview

DriftFlow is a minimal workflow engine used by multiple internal teams. It provides:

- deterministic execution order (by priority, then name)
- configurable retry attempts per step
- JSON file storage backend
- optional audit logging for every step

## Execution model

Workflows are executed step-by-step. Steps are sorted by **descending priority** (highest first), then **alphabetically by name**. Retries (`max_attempts`) are applied only to non-optional steps. Optional steps always get exactly 1 attempt and do not stop the workflow on failure.

Non-optional step failures stop the workflow immediately.

## Storage

The storage layer persists audit events (when the `audit` flag is enabled). JSON append-only file storage is the only implemented backend. Each event is written as a JSON line with a timestamp.

## Feature Flags

Feature flags default to **disabled**. The `audit` flag controls whether step events are written to storage. Other known flags (`metrics`, `parallel`) are defined but not currently used by the engine.
