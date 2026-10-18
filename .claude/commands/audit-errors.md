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
- Only edit $ARGUMENTS. Do not modify utils/errors.py, routes/api.py, or services/users.py (unless it is $ARGUMENTS).
- Do not add new AppError subclasses - use only the existing ones.
-Preserve all function signatures, seed data, and constants.

## Verification
Run "pytest -q" after every function you change; all tests must pass before moving to the next function. Finish with
"pytest -v" and "git diff --stat", and confirm only $ARGUMENTS changed. List each function as "changed" or "no change
needed".
