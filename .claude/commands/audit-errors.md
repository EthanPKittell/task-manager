## Goal
Audit $ARGUMENTS for missing AppError handling. For every function that raises a raw exception
(ValueError, KeyError, TypeError, etc.) for arguments matching its type hints, including unguarded
lookups like TASKS[task_id], replace it with the matching AppError subclass from utils/errors.py.

## Context
- Canonical pattern: get_user in services/users.py (check membership, raise NotFoundError("User")).
- AppError hierarchy: utils/errors.py - AppError, NotFoundError(resource), ValidationError(field, reason).
- Services contain business logic only: no flask imports, no HTTP status codes. routes/api.py converts 
AppError to JSON via handle_app_error, so routes never catch errors.

## Constraints
- Idempotency: if a function already uses AppError correctly (for every argument matching its type hints
it raises only AppError subclasses), skip it - do not rewrite, reformat, or add tests for it. Report it as
"no change needed".
- Arguments that violate the type hints are out of scrope: list them under "Out of scope", do not fix.
- Scope lock: only edit $ARGUMENTS, plus append tests to tests/test_tasks.py. Never modify utils/errors.py,
routes/api.py, or app.py.
- Do not add new AppError subclasses. Preserve all function signatures, seed data, and constants.
- When you change a function, update its docstring Raises: section to match.

## Verification
Test-first, after every function - not when done: append a failing test to tests/test_tasks.py, run pytest -q
and print the summary line (expect 1 failure), fix the function, run pytest -q and print the summary line
(expect all to pass), then move to the next function. Finish with pytest -v and git diff --stat (only $ARGUMENTS
and tests/test_tasks.py). List each function as "changed", "no change needed", or "out of scope".
