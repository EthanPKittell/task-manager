## Goal
Scaffold a new API endpoint from $ARGUMENTS, given as "<resource> <METHOD>" (e.g. "tags POST"):
the first word is the resouce name, the second is the HTTP method. When done:
- Route file: routes/api.has one new route for <METHOD> /<resource>.
-Service file: services/<resource>.py has the function the route calls (create the file if missing,
with an in-memory seed dict like TASKS in services/tasks.py).
- Schema file: schemas/<resource>.py has a TypeDict describing the record's fields (create
schemas/__init__.py if missing).
- Tests: new tests appended to tests/test_tasks.py.

## Context
- Canonical pattern: routes/tasks.py. In this project the task routes live in routes/api.py:
create_task_route (POST -> 201) and list_tasks_route /update_task_route (type hints, Google-style
docstrings). Service pattern: services/tasks.py and get_user in services/users.py.
- app.py mounts the blueprint at /api, so the URL is /api/<resource>.
- handle_app_error in routes/api.py turns any AppError into a JSON error; routes never catch errors.
- Route tests use app.test_client(), as in tests/test_tasks.py.

## Constraints
- No business logic in the route handler: it only reads request.get_json(), request.args, or URL params,
calls exactly one service function, and returns jsonify(...) with a status code. No validation, no
branching on data values, no try/except, no dict mutation in routes.
- All validation and data changes live in services/<resource>.py, raise only AppError subclasses from
utils/error.py, and never import flask.
- Do not modify existing routes, existing service functions, seed data, or utils/errors.py.
- Test-first (CLAUDE.md): append tests to tests/test_tasks.py and confirm they fail before writing the
route or service.
- If the resouces's fields are unspecified, state your assumption in one line, then proceed.
- For methods with a JSON body, the route passes the whole body to the service (service(request.get_json())),
exactly like update_task_route. The route never calls .get() or indexes the body; the service checks the body
is a dict and raises ValidationError if not.

## Verification
1. Run pytest -q after the tests are appended (expect failures) and after every file you change.
2. Include a happy-path route test asserting the correct status: 201 for POST, 200 for GET/PATCH, and
a test that a non-object body (e.g. []) returns 422.
3. Finish with pytest -v, ruff check . (only the known pre-existing errors), and git status --short
(it shows new untracked files too); only the files named in the Goal may appear.
