# WORKFLOW_LOG.md

Features: **B (due dates)** and **C (archiving)**. Both change "list_tasks()" and "GET /api/tasks", which already had a priority filter, so the merge had to reconcile two independent designs of the same listing logic.

## Running in parallel

Each feature ran in its own Claude Code session and worktree: 

- Terminal 1: "claude --worktree due-dates" -> branch "worktree-due-dates"
- Terminal 2: "claude --worktree archiving" -> branch "worktree-archiving"

"git worktree list" while both sessions were active:
"""
PS C:\AI_Agents_5300\PA8\task-manager>    git worktree list
C:/AI_Agents_5300/PA8/task-manager                              f80c310 [main]
C:/AI_Agents_5300/PA8/task-manager/.claude/worktrees/archiving  f80c310 [worktree-archiving] locked
C:/AI_Agents_5300/PA8/task-manager/.claude/worktrees/due-dates  f80c310 [worktree-due-dates] locked
"""

The session timestamps also show the overlap. Both plans were finished at 6:12-6:13 PM, both failing test runs were recorded at 6:19 PM, both implementations finished at 6:22-6:23 PM, and both feature commits are timestamped 18:41. 

Neither session could see the other's work, and that mattered at plan review (below): both plans independently added a second positional parameter to "list_tasks", which only I could see.

---

## Feature B: due dates ("worktree-due-dates")

### 1. Plan (plan mode) and the change I requested

During planning, Claude asked me three design questions and I chose:
- **Overdue** = past due and not done; a task due today is not overdue.
- **"?overdue=false"** returns the tasks that are not overdue.
- **PATCH "{"due_date": null}"** clears the due date.

The first plan also made tests independent of the real date (a "today" parameter plus a "_today()" helper that route tests monkeypatch). I rejected it and requested this change:
 
> Change the plan: make overdue a keyword-only parameter, "list_tasks(priority=None, *, overdue=None, today=None)", and call it by name everywhere: the route passes "overdue=request.args.get("overdue")", and tests always use "overdue=..." by keyword. Reason: another branch is adding its own filter parameter to list_tasks in parallel. Positional calls would bind to the wrong parameter after the merge.
> Also state explicitly in Step 2 that update_task accepts a body containing only due_date, and that the error for a body with none of the accepted fields keeps its exact existing message, so no existing test changes.

**Why:** the plan's route called "list_tasks(request.args.get("priority"), request.args.get("overdue"))", with "overdue" as the second *positional* parameter. The archiving branch was adding its own second parameter at the same time. After the merge, every positional call from one branch would pass its value to the other branch's filter, silently in some cases. Also, Step 2 of the first plan didn't say how "update_task"'s existing "must include priority or title" check would handle a body containing only "due_date".

The revised plan made "overdue" and "today" keyword-only, added a test that "list_tasks(2, True)" raises "TypeError" to lock that in, and spelled out the "update_task" rules. I approved it.

### 2. Tests first: the failing run

Claude appended the tests, ran pytest and stopped:
"""
! pytest -q
........................................................................ [ 28%]
........................................................................ [ 56%]
...................................................................FFFFF [ 85%]
… +479 lines

Your run matches mine: 40 failed, 214 passed. All 211 existing tests pass, and the 40 new tests fail for the expected reasons: due_date, overdue/today and _today don't exist yet. The other 3 new tests pass by design because they lock in the existing behavior.

I haven't touched any app code. Say "go" and I'll implement Step 2 (services/tasks.py) and then Step 3 (routes/api.py), running pytest -q after each file.
 
"""
All 211 existing tests still passed. The 40 new failures had the expected causes: "create_task" didn't accept "due_date", "list_tasks" didn't accept "overdue"/"today", "services.tasks._today" didn't exist, "update_task" rejected a body containing only "due_date", and POST ignored "due_date". Three new tests passed already **by design**: they lock in existing behavior (the exact "must include priority or title" message for "{}" and "{"foo": 1}", and that the second argument is keyword-only).

### 3. Implementation

"Implement the plan until pytest -q passes. Do not change any existing test." Claude changed "services/tasks.py" (validation helpers, "create_task", "update_task", "list_tasks") and then "routes/api.py" (POST and GET pass the values through, with no validation in the route). My run afterwards:
"""
! pytest -q
254 passed in 0.91s
"""

### 4. "/diff" review and what I corrected

During the final checks ruff flagged "date.today()" in "_today()" (DTZ011, no timezone). Claude asked how to handle it, and I accepted its recommendation, "Use UTC date", so "_today()" became "datetime.now(timezone.utc).date()". 

Reviewing "/diff", I saw this was a **behavior change, not a lint fix**: with UTC, a task due "today" in New York counts as overdue from 7-8 PM local time, because UTC midnight comes first. Users mean their own local date when they say "overdue". I had Claude change it to "datetime.now().astimezone().date()", which returns the local date and still passes ruff's DTZ rules, and update the docstring. pytest still passed.
"""
❯ In /diff I found a problem: _today() now returns the UTC date, so in New York a task due today becomes overdue at 7-8 pm local time. Change it to return datetime.now().astimezone().date() (the local date; it also satisfies ruff's DTZ rules), update its docstring to say "local date", and remove the timezone import if it's no longer used. Then run pytest -q and ruff check .

● Update(services\tasks.py)
Added 2 lines, removed 2 lines
        None.

    Returns:
        The current date in UTC.
        The current local date.

    Raises:
        None.
    """
    return datetime.now(timezone.utc).date()
    return datetime.now().astimezone().date()

def _validate_due_date(due_date: str | None) -> None:
    """Check that a due date is None or a real date in "YYYY-MM-DD" format.
...
"""

Also checked in "/diff": seed "TASKS" unchanged; no existing test edited; the route has no validation or "try/except"; "update_task" validates every field before changing anything (no partial updates); docstrings have Args/Returns/Raises; only the three planned files changed. 

Side note: when Claude first tried to append the tests with a shell heredoc ("cat >... << EOF"), the command was refused, and it switched to the Edit tool. That's the better outcome, because edits made with the Edit tool are tracked by "/rewind" and shell writes aren't.

### 5. Commits ("/ship")

| Commit | Message |
|---|---|
| "fcfaa8e" | "feat(tasks): add due dates and overdue filter" |

One commit: tests and code together, as CLAUDE.md requires ("routes/api.py", "services/tasks.py", "tests/test_tasks.py"; 325 insertions, 25 deletions). "/ship" ran its debug check and "pytest -q", proposed the message, and Claude Code asked me to confirm the "git commit" before it ran.

---
 
## Feature C: archiving ("worktree-archiving")

### 1. Plan (plan mode) and the change I requested

The first plan was already careful: tests archive only tasks they create, "archive_task" reuses "get_task" (so an unknown id raises "NotFoundError"), archiving is idempotent, "include_archived" accepts only "true"/"false", and "POST /api/tasks/<id>/archive" was added. But it used "list_tasks(priority, include_archived)" with a **positional** second parameter, and test 6 called "list_tasks(4, True)". I rejected it and requested: 

> Change the plan: make include_archived a keyword-only parameter, "list_tasks(priority=None, *, include_archived=None)", and call it by name everywhere: the route passes "include_archived=request.args.get("include_archived")", and tests use "list_tasks(4, include_archived=True)", never "list_tasks(4, True)". Reason: another branch is adding its own filter parameter to list_tasks in parallel. Positional calls would bind to the wrong parameter after the merge.

**Why:** the same reason as Feature B. After merging, "list_tasks(4, True)" would have meant "priority 4 and overdue" instead of "include archived". The revised plan made the parameter keyword-only and added a rule that every new test passes it by name. I approved it.

The plan also flagged a risk I left as is: the existing "test_get_tasks_by_status_covers_all_tasks" assumes done + pending = "len(list_tasks())", which stops being true once a task is archived. It passes only because the new tests run after it. Claude didn't edit it (CLAUDE.md forbids that), and I agreed.
 
### 2. Tests first: the failing run

"""
ERROR collecting tests/test_tasks.py
E   ImportError: cannot import name 'archive_task' from 'services.tasks'
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.91s
"""
I reran "! pytest -q" myself and got the same collection error. This is the expected failing run for this feature: CLAUDE.md requires imports in the top import block, and "archive_task" didn't exist yet, so the test file couldn't load. It's a single collection error rather than 12 separate failures.
 
### 3. Implementation

Same instruction as Feature B. Claude added "archive_task", "_parse_include_archived" and the "include_archived" filter to "services/tasks.py", then the route changes and "archive_task_route" to "routes/api.py". My run afterwards:
"""
! pytest -q
231 passed in 0.94s
"""

### 4. "/diff" review

I didn't need to correct anything in this diff. What I checked:
- "include_archived" is keyword-only in the signature, the route and every new test (no "list_tasks(4, True)").
- Every new test archives only tasks it created; seed tasks 1-3 are never archived, so "test_list_tasks_all" still holds.
- Seed "TASKS" unchanged; a missing ""archived"" key counts as not archived.
- The routes only pass raw values; "NotFoundError" reaches "handle_app_error" with no "try/except".
- "archive_task" has a full docstring, including "Raises: NotFoundError" (my CLAUDE.md requires it).
- Only the three planned files changed; no existing test edited.

### 5. Commits ("/ship")

| Commit | Message |
|---|---|
| "a69b259" | "feat(tasks): add task archiving" |

One commit ("routes/api.py", "services/tasks.py", "tests/test_tasks.py"; 188 insertions, 17 deletions), with the same "/ship" checks and a permission prompt for "git commit".