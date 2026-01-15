# DriftFlow Design Notes

## Overview

DriftFlow is a minimal workflow engine used by multiple internal teams. It provides:

- deterministic execution order
- retry with exponential backoff
- pluggable storage backends (sqlite, memory)
- audit logging for every step

## Execution model

Workflows are executed step-by-step. Steps are executed in FIFO order and retries are applied per step. Optional steps are still retried to preserve deterministic behavior.

## Storage

The storage layer persists audit events and workflow results. SQLite is the default backend, but an in-memory backend is available for tests.

## Backward compatibility

The `retries` field is preserved for backward compatibility with older configs.
