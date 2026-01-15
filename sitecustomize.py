"""Test runner conveniences.

This small hook makes `python -m unittest` (with no args) behave like
`python -m unittest discover` when run from the project root. Python automatically
imports `sitecustomize` if present on `sys.path`.
"""
from __future__ import annotations

import os
import sys


def _is_unittest_cli_invocation() -> bool:
    # When invoked as `python -m unittest`, argv[0] typically ends with `unittest` or `unittest/__main__.py`
    target = os.path.basename(sys.argv[0] or "")
    return target in {"unittest", "__main__.py"} and "unittest" in (sys.argv[0] or "")


# If no extra args were provided, default to discovery so `python -m unittest`
# executes the suite. This is a no-op for other commands.
if _is_unittest_cli_invocation() and len(sys.argv) == 1:
    sys.argv.append("discover")
    sys.argv.extend(["-s", "tests"])
