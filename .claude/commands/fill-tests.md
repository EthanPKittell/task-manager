# Use this when a services file has functions with missing tests in tests/test_tasks.py; do not use it for a new feature (write those tests in the feature's own session) or when app code needs changing.

## Goal
For every public function in $ARGUMENTS, make sure tests/test_tasks.py has at least one
happy-path test and, if the function can raise an AppError, one test for that error.
Append tests for every gap found.

## Context
- Tests live only in tests/test_tasks.py in the existing bare style (no docstrings).
- Tests share module state (TASKS, USERS): create your own records or restore what you change;
never depend on test order. SA-4 in DECOMPOSITION.md is the reference session for this task.
- AppError hierarchy: utils/errors.py. Route tests use app.test_client().

## Constraints
- Append only to tests/test_tasks.py; you may extend the import block at the top. Never edit 
or delete existing tests.
- Do not modify $ARGUMENTS or anything in services/, routes/, or utils/.
- Only test arguments that match the type hints.
- If a new test fails, stop and report it; do not change app code or weaken the test.
- If there are no gaps, report "no gaps" and change nothing.

## Verification
Before writing anything, run git status --short and record it as the baseline; at the end,
report only what changed relative to that baseline. Print a table of each function as
"covered" or "gap: <what's missing>". Run pytest -q after each function's tests are appended;
all must pass. Finish with pytest -v, ruff check . --output-format concise (confirm the errors
are exactly the known pre-existing ones), and git status --short showing only
tests/test_tasks.py changed beyond the baseline. When appending, match the file's existing
line endings (CRLF).