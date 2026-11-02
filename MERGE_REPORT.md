# MERGE_REPORT.md


Both feature branches were merged into "main" locally with "git merge --no-ff", keeping git's default merge messages (allowed by my commit-msg hook):

1. "git merge --no-ff worktree-due-dates" -> **clean**, merge commit "d74e6ad" 
2. "git merge --no-ff worktree-archiving" -> **conflicts in 3 files (6 blocks)**, resolved with Claude, merge commit "fd90452"

I asked Claude to explain every conflict and propose a resolution **without editing any file until I approved**. The behavioral decisions below are mine.

## Conflicts
 
### "services/tasks.py": 3 blocks

**Block 1: new helpers in the same spot (after "get_tasks_by_status")**
- *Due dates (HEAD):* "_today()", "_validate_due_date()", "_parse_overdue()", "_is_overdue()".
- *Archiving:* "archive_task()" and "_parse_include_archived()".
- *Resolution:* keep all six. No overlap; git only conflicted because both sides inserted at the same place.

**Block 2: the "list_tasks" signature**
- *Due dates:* added keyword-only "overdue" and "today".
- *Archiving:* added keyword-only "include_archived".
- *Resolution:* "list_tasks(priority=None, *, overdue=None, include_archived=None, today=None)". Because I'd made both parameters keyword-only at plan review, this was a clean union; no call site had to change. 

**Block 3: the "list_tasks" docstring and body**
- *Due dates:* validated priority, then overdue; filtered by priority, then overdue; no archive check.
- *Archiving:* validated "include_archived" *first*, then priority; one list comprehension that dropped archived tasks; no overdue check.
- *Resolution:* one body that validates every value first, then applies the filters one after another:
  ```python
  overdue = _parse_overdue(overdue)
  include_archived = _parse_include_archived(include_archived)
  tasks = list(TASKS.values())
  if not include_archived:
      tasks = [task for task in tasks if not task.get("archived", False)]
  if priority is not None:
      tasks = [task for task in tasks if task["priority"] == priority]
  if overdue is not None:
      if today is None:
          today = _today()
      tasks = [task for task in tasks if _is_overdue(task, today) is overdue]
  return tasks
  ```
  The docstring summary became "Retrieve tasks, optionally filtered by priority, overdue status and archived state.", with Args/Raises covering all three filters.

### "routes/api.py": 2 blocks

- **Docstring of "list_tasks_route":** each side documented only its own query parameter -> merged to cover priority, overdue and include_archived.
- **Route body, plus the new route:** due dates passed "overdue..."; archiving passed "include_archived=..." and added "POST /tasks/<id>/archive" -> the route now passes all three by keyword, and "archive_task_route" is kept unchanged. The route still only reads query values; all validation stays in the service (the layer rule in CLAUDE.md).
 
### "tests/test_tasks.py": 1 block

Both branches appended tests at the end of the file. *Resolution:* keep both blocks in full.

**A merge hazard Claude caught:** the last two lines of the conflict region ("assert response.status_code == 422" / "assert "error" in response.get_json()") were identical on both sides, so git placed them **outside** the conflict markers, attached only to archiving's last test. Resolving the conflict by simply keeping both sides would have left due dates' last test, "test_list_tasks_route_invalid_overdue", making a request and **asserting nothing**. It would still pass, and that's exactly the problem: a silently weakened test. Claude restored the two asserts, and I checked both final tests:
```python
def test_list_tasks_route_invalid_overdue(monkeypatch) -> None:
    monkeypatch.setattr(tasks_service, "_today", lambda: FIXED_TODAY)
    response = app.test_client().get("/api/tasks?overdue=maybe")
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_list_tasks_route_invalid_include_archived() -> None:
    response = app.test_client().get("/api/tasks?include_archived=yes")
    assert response.status_code == 422
    assert "error" in response.get_json()
```

## Final behavior: my decisions

1. **All filters must match (AND).** "?priority=2&overdue=true" returns tasks that are priority 2 *and* overdue.
2. **Archived tasks stay hidden even for "?overdue=true", unless "include_archived=true".** Archiving means "take this out of my active views", and an overdue list is an active view. Showing archived work there would undo the reason for archiving it. 
3. **Validation order: priority, then overdue, then include_archived.** When several values are invalid, the first one in this order produces the 422. Priority keeps its original position, and the new filters follow in the order the branches were merged. This changed the archiving branch, which used to check "include_archived" first; no test depends on the order.
4. **Seed tasks** have no "due_date" or "archived" key and count as not overdue and not archived (unchanged from both branches).

## Tests

**No existing test was changed or removed.** I compared every test function in the merge commit with both branches: all 129 tests from "worktree-due-dates" and all 118 from "worktree-archiving" are present and identical in "fd90452".

**Two tests added** to cover both features together, which neither branch could test on its own:
- "test_list_tasks_overdue_hides_archived_unless_included" (service): an archived task due 2026-06-14 is excluded from "list_tasks(overdue=True, today=date(2026, 6, 15))" and included when "include_archived=True" is added.
- "test_list_tasks_route_overdue_hides_archived_unless_included" (route, with "_today" monkeypatched): the same check through "?overdue=true" vs "?overdue=true&include_archived=true".

These two were **not seen failing first**. Claude wrote them before resolving "services/tasks.py", but pytest couldn't collect anything while conflict markers remained, and once the conflict was resolved the merged code already behaved as they expect. They lock in decision 2 rather than drive it.

**Known fragility (unchanged):** "test_get_tasks_by_status_covers_all_tasks" assumes done + pending = "len(list_tasks())". Since archived tasks are now hidden from "list_tasks()", that holds only because the archive tests run after it in file order. Claude flagged it during archiving's plan and again during the merge. I left it alone because CLAUDE.md forbids editing existing tests. The real fix (test isolation, or redefining that test) belongs in a separate, reviewed change. 

## Final test run

After resolving the conflicts (my own run):
```
! pytest -q
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
............................................................             [100%]
276 passed in 0.99s
```
276 = 211 existing + 43 (due dates) + 20 (archiving) + 2 (combined). Before committing, I ran "ruff check ." (only the 6 known errors) and "git diff --check" (no output). I then completed the merge myself with "git commit --no-edit", and "pytest -q" on the merge commit still shows 276 passed.
