# DriftFlow Design Notes

## Overview

DriftFlow is a minimal workflow engine used by multiple internal teams. It provides:

- deterministic ordering based on priority then name
- bounded attempts per step (no exponential backoff)
- append-only JSON file storage for audit events
- opt-in audit logging (via the `audit` flag)

## Execution model

Steps are materialized from the config, sorted by `priority` (higher first) and `name`, then executed. Non-optional steps respect `max_attempts` (default 1) and stop the workflow on the first failure. Optional steps always run once and do not block later steps even when they fail. A step with an unknown `action` raises and is recorded as a failed result.

## Storage

The storage layer currently persists audit events as JSON lines in a single file path provided by config. The path is created if missing. There is no alternative backend in the current implementation.

## Compatibility

The historical `retries` field is no longer consumed; use `max_attempts` to control retry attempts.
