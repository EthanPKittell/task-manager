# Task Manager

Python Flask API for managing tasks and users.

## Commands
- If a tool needs to be downloaded assume powershell is being used. If the user is using wsl prompt them to switch to powershell as nothing in this project is linux specific
- Install commands: `pip install -r requirements.txt`
- Run tests: `pytest -v`
- Lint: `ruff check .`
- Run server: `python app.py`
- Run: `pytest -v` and `ruff check .` before finishing any tasks

## Architecture
- We use @routes/api.py to handle HTTP only and it calls @services/
- @services/ is the business logic. @services/users.py is the standard example.
- Data lives in dictionaries within @services/tasks.py and @services/users.py. Only services functions read or write to tese dictionaries.
- @utils/errors.py is the AppError hierarchy. The "handle_app_error" within @routes/api.py turns any AppError into a json error message so services raise errors and routes never have to catch them.


## Conventions
- Follow @services/users.py for "get_user" lookups
- Type hints must be on every function
- Google-style docstrings are required on every function with "args:", "Returns: ", and "Raises: " sections that match "get_user" from @services/users.py
- Raise only "AppError" subclasses from @utils/errors.py never raise raw exceptions
- New tests must be put in @tests/test_tasks.py

 
## Do not touch
- In @utils/errors.py do not change "AppError.__init__" or the existing subclasses. Add a new subclass ONLY if no existing one fits.
- For existing tests in @tests/test_tasks.py never edit or delete them to make a change pass always fix the code instead.


