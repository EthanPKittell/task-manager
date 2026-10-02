## Justificiation
Ethan Kittell 10/1/26

### Commands

The commands section changed the most of all sections, almost every change came from a failure. In Session 1 Claude ran the `pytest -v` command but skipped `ruff check .` because ruff was not installed, because of this I added sudo install rules and a install_commands.txt. In session 2 I found that this fix had an issue: Claude Code commands run without an interactive terminal, so sudo could never prompt me from my password. I replaced all of this wil pip install -r requirements.txt after adding "ruff=0.16.9" to requirements.txt, which is what Claude suggested I do in session 1. To halve this section I would keep the install, test and lint commands and get rid of the run-server and PowerShell lines.

### Architecture

The architecture section names the files Claude chooses between. The "/routes/api.py" for HTTP, "/services" for logic, and "/utils/errors.py" for the AppError hierarchy. The handle_app_error line mattered the most, because it tells Claude that services raise errors and routes never catch them which is why every session put error handling in "/services/tasks.py". In sessions 2 and 3, Claude called get_user to check that a user existend instead of reading USERS directly, following my rule that only service functions touch the data dictionaries. To halve this section, I would keep the "errors.py" and "/services/users.py" lines and cut the dictionary line. 

### Conventions

Every convention names something Claude can copy instead of an abstract style. In session 1, get_task got a Google-style docstring with Args, Returns and Raises, plugs an "if task_id not in TASKS" check raising NotFoundError("Task"), copied directly from "get_user". Session 2 did show a side effect: to give the required Raises section something real, Claude added a "ValidationError" for blank titles and a "NotFoundError" for missing users, changing create_task's behavior for a style only change prompt. To halve this section I would keep the "/services/users.py" and AppError rules, since the docstring and type-hint rules mostly follow from copying "get_user".


### Do not touch

I limited this section to two rules protecting things the project depends on like the AppError constructors and the existing "/tests/test_tasks.py". Session 3 tested the second rule directly when the ruff lint failed. If I had to cut one rule, I would drop the errors.py rule, because no session came close to editing that file.


### Team use

For a team of three developers I would move machine specific rules like my PowerShell-versus-WSL line into each developer's CLAUDE.local.md. The shared file would keep only commands that work everywhere such as `pip install -r requirements.txt` in a virtual environment. My session 1 and 2 failures came from rules written for one machine. Second I would replace "ask the user how to handle each linter error" with a written policy, like fixing lint only in changed lines and keeping the rest. Otherwise three developers would give Claude three different answers about the same six ruff answers.