# Task Manager

Python Flask API for managing tasks and users.

## Commands
- If a tool needs to be downloaded assume powershell is being used. If the user is using wsl prompt them to switch to powershell as nothing in this project is linux specific
- Install commands: `pip install -r requirements.txt`
- Run tests: `pytest -v`
- Perform a quick test run after each file edit: `pytest -q` (use `pytest -v` for the final run)
- Check scope after any change: `git diff --stat` this has to list the files the task names
- Lint: `ruff check .`. Do not fix a lint error yourself. Ignore the 6 known pre-existing errors (I001 in app.py, routes/api.py and tests/test_tasks.py; F401 unused process_order import in routes/api.py; B017 x2 in tests/test_tasks.py). Report any other error and then ask the user how to handle them.
- Run server: `python app.py`
- Run: `pytest -v` and `ruff check .` before finishing any tasks

## Architecture
- We use @routes/api.py to handle HTTP only and it calls @services/
- @services/ is the business logic. @services/users.py is the standard example.
- Data lives in dictionaries within @services/tasks.py and @services/users.py. Only services functions read or write to test dictionaries.
- @utils/errors.py is the AppError hierarchy. The "handle_app_error" within @routes/api.py turns any AppError into a json error message so services raise errors and routes never have to catch them.
- Layer boundary: @routes/api.py only pulls values out of the request (request.get_json(), request.args) and passes plain Python values to a @services/ function; @services/ never imports flask, reads the request, or returns HTTP responses or status codes, and signals errors only by raising AppError subclasses. @services/users.py (get_user, get_notification_pref) and their routes in @routes/api.py are the canonical pattern.


## Conventions
- Follow @services/users.py for "get_user" lookups
- Type hints must be on every function
- Google-style docstrings are required on every function with "Args:", "Returns: ", and "Raises: " sections that match "get_user" from @services/users.py
- Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions
- New tests must be put in @tests/test_tasks.py
- Test first for every feature or bug fix: write the new tests in @tests/test_tasks.py, run 'pytest -q' and confirm the new tests fail before editing any file in @services/ or @routes/, implement, running 'pytest -q' after each file edit, finish with a final 'pytest -v' run.

 
## Do not touch
- In @utils/errors.py do not change "AppError.__init__" or the existing subclasses. Add a new subclass ONLY if no existing one fits.
- For existing tests in @tests/test_tasks.py never edit or delete them to make a change pass always fix the code instead.
- When a task is scoped to tests only, do not edit @services/, @routes/, or @utils/. In @tests/test_tasks.py only append new tests and extend the import block at the top of the file if a new test fails, stop and report it instead of changing any app code.
- When a task is scoped to the API layer, do not edit @services/users.py or @services/tasks.py to make a route fit, and do not add validation or try/except to @routes/api.py. If a service signature doesn't cover a request case (e.g. a body that isn't a JSON object), stop and then report the gap.
- Do not change the seed data (USERS in @services/users.py, TASKS in @services/tasks.py) or the constants NOTIFICATION_PREFS, DEFAULT_NOTIFICATION_PREF, and DEFAULT_PRIORITY unless the task explicitly asks; existing tests in @tests/test_tasks.py depend on them.


