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
- If a function already raises only AppError subclasses correctly, skip it - do not rewrite, reformat,
or "improve" it. Report it as "no change needed".
- Only edit $ARGUMENTS, plus append new tests to tests/test_tasks.py. Touch no other file. Do not modify
utils/errors.py, routes/api.py, or services/users.py (unless it is $ARGUMENTS).
- For each function you change, follow CLAUDE.md test-first: append a test to tests/test_tasks.py that expects the AppError,
confirm it fails, then fix the function. Never edit or delete existing tests.
- Do not add new AppError subclasses - use only the existing ones.
-Preserve all function signatures, seed data, and constants.

## Verification
For each function you change: run pytest -q after the failing test is added (expect 1 failure),
then again after the fix (expect all pass), and print the pytest -q summary line both times
before moving to the next function. Finish with pytest -v and git diff --stat; confirm only
$ARGUMENTS and tests/test_tasks.py changed. List each function as "changed" or "no change needed".
