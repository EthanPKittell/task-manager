## Goal
Audit $ARGUMENTS for missing AppError handling. For every function that raises a raw exception (ValueError, KeyError, TypeError, etc) or elts one escape
(e.g. an unguarded dict lookup like TASKS[task_id]), replace it with the matching AppError subclass from utils/errors.py, so the function raises only
AppError subclasses.

## Context
- Canonical pattern: get_user in services/users.py (check membership, raise NotFoundError("User")).
- AppError hierarchy: utils/errors.py - AppError, NotFoundError(resource), ValidationError(field, reason).
- Services contain business logic only: no flask imports, no HTTP status codes. routes/api.py converts
AppError to JSON via handle_app_error, so routes never catch errors.

## Constraints
- A function is already correct if, for every argument that matches its type hints, it raises
only AppError subclasses. Skip it - do not rewrite, reformat, or add tests for it - and
report it as "no change needed".
- Arguments that violate the type hints (e.g. a list for user_id: int, an int for name: str)
are out of scope. If you notice one, list it under "Out of scope" in your report; do not fix it.
- Only edit $ARGUMENTS, plus append new tests to tests/test_tasks.py. Touch no other file. Do not modify
utils/errors.py, routes/api.py, or services/users.py (unless it is $ARGUMENTS).
- For each function you change, follow CLAUDE.md test-first: append a test to tests/test_tasks.py that expects the AppError,
confirm it fails, then fix the function. Never edit or delete existing tests.
- Do not add new AppError subclasses - use only the existing ones.
-Preserve all function signatures, seed data, and constants.
- When you change a function, update its docstring Raises: section to match (add one if missing).
- If you find a raw exception in another file, list it under "Out of scope" in your report - do not fix it.

## Verification
For each function you change: run pytest -q after the failing test is added (expect 1 failure),
then again after the fix (expect all pass), and print the pytest -q summary line both times
before moving to the next function. Finish with pytest -v and git diff --stat; confirm only
$ARGUMENTS and tests/test_tasks.py changed. List each function as "changed" or "no change needed".
