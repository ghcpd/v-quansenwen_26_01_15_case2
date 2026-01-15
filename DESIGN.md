# DriftFlow Design Notes

## Overview

DriftFlow is a minimal workflow engine used by multiple internal teams. It provides:

- Priority-based execution order (sorted by priority descending, then name ascending)
- Configurable retry attempts for non-optional steps
- JSON file storage backend for audit logging
- Feature flags to control runtime behavior

## Execution model

Workflows are executed step-by-step after sorting by priority and name. Retries are applied per step based on `max_attempts` configuration (default: 1, meaning no retries). Optional steps are executed exactly once without retries.

If a non-optional step fails after all attempts, the workflow **stops** and remaining steps are skipped.

## Storage

The storage layer persists audit events. The current implementation uses an append-only JSON file (`JsonFileStorage`). Each event is written as a single JSON line with a timestamp.

## Feature flags

Known flags: `audit`, `metrics`, `parallel`.

All flags are **disabled by default** and must be explicitly enabled in the config. The `parallel` flag is recognized but not currently implemented.

## Backward compatibility

The `max_attempts` field controls retry behavior. Legacy configs using `retries` will not work as expected; they should be updated to use `max_attempts`.
