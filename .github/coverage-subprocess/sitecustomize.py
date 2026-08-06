"""Subprocess coverage measurement hook — CI-only, see DECISIONS.md D-024.

Python's ``site`` module automatically imports a module named
``sitecustomize`` at interpreter startup if one is found on ``sys.path``.
CI adds this directory to ``PYTHONPATH`` only for the pytest step that
measures coverage, so every subprocess spawned during that step (in
particular the CLI-level tests in tests/test_validation.py, which run
``python scripts/validate.py ...`` in a fresh interpreter) picks this up
too, and starts recording its own coverage data.

``coverage.process_startup()`` is intentionally a no-op unless the
``COVERAGE_PROCESS_START`` environment variable is also set (to
``.coveragerc``, by the same workflow steps) — so importing this module
anywhere else, or with that variable unset, has no effect.
"""

import coverage

coverage.process_startup()
