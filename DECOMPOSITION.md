# Task 2- Notification preference pipeline

Feature: users can set notification_pref to "email", "sms", or "none" (default "none")
Note: the spec says the "existing user list endpoint" must include notification_pref, the codebase has no user list endpoint, so for SA-2/SA-3 add list_users and GET /users.
Note: SA-1-SA-3 are told not to write tests (SA-4 only), which overrides the CLAUDE.md "test first" rule for this pipeline only.

## SA-1: Data layer

| Field | Value |
| ----  | ----- |
| Subagent # | SA-1: Data layer |
| Input | services/users.py, CLAUDE.md |
| Task | Add the notification_pref field to every user record with a default of "none" |
| Output | services/users.py (modified). **result:** pytest -q -> 97 passed. git diff --stat showed only services/users.py; no tests written, no new functions. |
| Constraint | Edit only services/users.py. Do not touch routes/api.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Do not add new functions; only add constants, update the USERS seed data, and update create_user. Do not write tests. |
| Hand-off | Constants NOTIFICATION_PREFS = ("email", "sms", "none") and DEFAULT_NOTIFICATION_PREF = "none" in services/users.py; every USERS entry and every user from create_user has "notification_pref": "none". |

**prompt:**
> SA-1 (data layer). In services/users.py only: add constants NOTIFICATION_PREFS = ("email", "sms", "none") and DEFAULT_NOTIFICATION_PREF = "none", add "notification_pref": "none" to every user in USERS, and make create_user store "notification_pref": DEFAULT_NOTIFICATION_PREF on new users. Do not add new functions. Do not touch routes/api.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Do not write tests in this session; SA-4 is responsible for writting tests. This overrides the CLAUDE.md test-first rule for this pipeline. Run pytest -q at the end. Follow all other CLAUDE.md conventions.

## SA-2: Service layer

| Field | Value |
| ----  | ----- |
| Subagent # | SA-2: Service layer |
| Input | services/users.py (with SA-1's constants), utils/errors.py, CLAUDE.md |
| Task | Add service function to read, update, and list notification preferences with validation |
| Output | services/users.py (modified). **result:** pytest -q -> 97 passed. git diff --stat showed only services/users.py; signatures and error message match the hand-off exactly; no tests written. Small note: the new functions are not yet covered by tests until SA-4. |
| Constraint | Edit only services/users.py. Do not touch routes/api.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Do not change get_user, create_user, the USERS seed data, or SA-1's constants. Never return HTTP responses or status codes; raise ValidationError / NotFoundError from utils/errors.py. Do not write any tests. |
| Hand-off | get_notification_pref(user_id: int) -> str; update_notification_pref(user_id: int, pref: str) -> dict (returns the updated user); list_users() -> list[dict]. Invalid pref (anything not in NOTIFICATION_PREFS, including None, non-strings, "EMAIL") raises ValidationError("notification_pref", "must be one of: email, sms, none"). Unknown user raises NotFoundError via get_user. |

**prompt:**

> SA-2 (service layer). In services/users.py only, add: get_notification_pref(user_id: int) -> str, update_notification_pref(user_id: int, pref: str) -> dict (returns the updated user), and list_users() -> list[dict]. Use get_user for lookups so unknown users raise NotFoundError. Reject any pref not in NOTIFICATION_PREFS (including None, non-strings, and wrong case like "EMAIL") with ValidationError("notification_pref", "must be one of: email, sms, none"). Validate before writing. Do not change get_user, create_user, USERS, or the existing constants. Do not touch routes/api.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Never return HTTP responses or status codes. Do not write tests in this session; SA-4 is responsible for tests. This overrides the CLAUDE.md test first rule for this pipeline. Run pytest -q at the end. Follow all other CLAUDE.md conventions.

## SA-3: API layer

| Field | Value |
| ----  | ----- |
| Subagent # | SA-3: API layer |
| Input | routes/api.py, services/users.py (SA-2's functions), CLAUDE.md |
| Task | Add GET /users, GET /users/<id>/notifications, and PATCH /users/<id>/notifications as HTTP-only routes. |
| Output | routes/api.py (modified). **result:** pytest -q -> 97 passed. git diff --stat was showing only changes to routes/api.py; routes call SA-2's functions by their exact hand-off names with no validation or try/except. Claude flagged that a PATCH body that isn't a JSON object (e.g. [] or null) won't return a clean 422 - a gap in the SA-2/SA-3 hand-off (see Divergence). |
| Constraint | Edit only routes/api.py. Do not touch services/users.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Do not modify existing task routes or get_user_route. No validation or try/except in routes; pass values to the service and let handle_app_error return errors. Do not write tests. |
| Hand-off | GET /api/users -> 200, list of users (each with notification_pref). GET /api/users/<id>/notifications -> 200, {"user_id": id, "notification_pref": pref}. PATCH /api/users/<id>/notifications with body {"notification_pref": "email"} -> 200, same shape; invalid or missing value -> 422; unknown user -> 404. |

**prompt:**
> SA-3 (API layer). In routes/api.py only, add: GET /users returning list_users(); GET /users/<int:user_id>/notifications returning {"user_id": user_id, "notification_pref": get_notification_pref(user_id)}; PATCH /users/<int:user_id>/notifications that reads notification_pref from the JSON body (missing key passes None) and returns {"user_id": ..., "notification_pref": ...} from update_notification_pref. Routes are HTTP only: no validation and no try/except; handle_app_error turns AppErrors into JSON. Type hints and Google-style docstrings on new routes. Do not modify existing task routes or get_user_route. Do not touch services/users.py, services/tasks.py, utils/errors.py, or tests/test_tasks.py. Do not write tests in this session; SA-4 owns tests. This overrides the CLAUDE.md test first rule for this pipeline. Run pytest -q at the end. Follow all other CLAUDE.md conventions.

## SA-4: tests
| Field | Value |
| ----  | ----- |
| Subagent # | SA-4: tests |
| Input | tests/test_tasks.py, services/users.py, routes/api.py, CLAUDE.md |
| Task | Append service and route tests for the notification preference feature. |
| Output | tests/test_tasks.py (appended). **results:** pytest -q -> 128 passed (97 existing + the 31 new ones). git diff showed only tests/test_tasks.py: 138 lines added, 0 removed, no existing tests edited. All new tests passed on the first run, so the stop and report rule never triggered. Claude disclosed one change beyond a pure append: a new `from services.users import (...)` block at the top of the file. |
| Constraint | Edit only tests/test_tasks.py; append only, never edit or delete existing tests. Do not touch services/, routes/, or utils/. If a new test fails, stop and report it; do not change app code or weaken the test without my approval. Match the existing bare tests style. |
| Hand-off | (Final subagent) Full suite green; test names listed in the summary.  |

**prompt:**
> SA-4 (tests). Append tests to tests/test_tasks.py only, matching the existing bare style. Cover: seed users and newly created users default to "none"; get_notification_pref and update_notification_pref for each valid value; invald values ("push", "", "EMAIL", None, 1) raise ValidationError and leave the pref unchanged; unknown user raises NotFoundError; list_users includes notification_pref; routes: GET /api/users, GET /api/users/<id> includes notification_pref, GET and PATCH /api/users/<id>/notifications (200, 422 for invalid or missing value, 404 for unknown user). Tests share module state, so restore any user pref you change or use membership assertions. Do not edit existing tests or touch services/, routes/, or utils/. If a new test fails, stop and report it; do not change app code. Run pytest -q, then pytest -v, then ruff check . and ask before fixing any new lint error.

## Divergence

**Did claude follow the constraint field for every subagent? If not, which constraint was violated and what did Claude do instead?**
Yes for the file boundaries they were followed. Every subagent was committed separately and 'git diff --stat' shows SA-1 and SA-2 only touched services/users.py, SA-3 only touched routes/api.py, and SA-4 only touched tests/test_tasks.py. SA-1 through SA-3 also followed the "do not write tests" rule that went above what CLAUDE.md says for "Test first for every feature or bug fix". One exception: SA-4's constraint said to "append only" but it added a "from services.users import (...)" at the top of tests/test_tasks.py. This was needed for the tests to run, and Claude disclosed it, but it shows that my constraint was worded too literally. 

**Did any subagent's output break the next subagent's assumption? How did you recover?**
Nothing broke outright but SA-3 used SA-2's exact function names and return values , and SA-4's 31 new tests passed on the first run. But the SA-2 to SA-3 hand-off left a bit of a gap. SA-2's update_notification_pref only takes "pref", so reading the request body has to happen in the route, while SA-3's constraint said "no validation in routes." SA-3 flagged that as non-object body wouldn't return a clean 422.

**Would you write the decomposition differently a second time? What would you change?**
First, I would define the edge case in the SA-3 hand-off: "a body that is not a JSON object returns 422," allowing "request.get_json(silent=True) or {}" as HTTP parsing rather than validation, and then add a matching case to SA-4.
Secondly, I would reconsider tests being last. After SA-1 to SA-3 saying "97 passed" provided nothing regressed; the new functions had no coverage until SA-4 (SA-2 even noted this). Having every layer write its own tests would match my CLAUDE.md's test first rule and catch problems earlier.
Thirdly, I would merge SA-1 and SA-2 into one sub agent. They edit the same file and their isolation doesn't have much benefit.
Lastly, I would word "append only" as "append tests; adding imports is allowed."