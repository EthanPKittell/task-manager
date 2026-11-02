import re
from datetime import date, datetime

from services.users import get_user
from utils.errors import NotFoundError, ValidationError

DEFAULT_PRIORITY = 3
TASK_CATEGORIES = ("work", "personal", "other")
DEFAULT_CATEGORY = "other"
MAX_TITLE_LENGTH = 200
_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
_UPDATE_FIELDS = ("priority", "title", "due_date")

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 1},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 5},
}

def process_order(task_id: int) -> dict:
    """Mark a task as done.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The updated task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    task = TASKS[task_id]
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    return TASKS[task_id]

def get_tasks_for_user(user_id: int) -> list[dict]:
    """Retrieve all tasks belonging to a user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A list of task records belonging to the user. Empty if the user has no tasks.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    get_user(user_id)
    return [task for task in TASKS.values() if task["user_id"] == user_id]

def get_tasks_by_status(status: str) -> list[dict]:
    """Retrieve all tasks with a given completion status.

    Args:
        status: The status to filter by, either "done" or "pending".

    Returns:
        A list of task records with the given status. Empty if no tasks match.

    Raises:
        ValidationError: If status is not "done" or "pending".
    """
    if not isinstance(status, str) or status not in ("done", "pending"):
        raise ValidationError("status", "must be one of: done, pending")
    done = status == "done"
    return [task for task in TASKS.values() if task["done"] is done]

def _today() -> date:
    """Return today's date. Tests replace this to pin the date.

    Args:
        None.

    Returns:
        The current local date.

    Raises:
        None.
    """
    return datetime.now().astimezone().date()

def _validate_due_date(due_date: str | None) -> None:
    """Check that a due date is None or a real date in "YYYY-MM-DD" format.

    Args:
        due_date: The due date to check. None means no due date.

    Returns:
        None.

    Raises:
        ValidationError: If due_date is not None and is not a string in
            "YYYY-MM-DD" format naming a real calendar date.
    """
    if due_date is None:
        return
    if isinstance(due_date, str) and _DATE_PATTERN.fullmatch(due_date):
        try:
            date.fromisoformat(due_date)
            return
        except ValueError:
            pass
    raise ValidationError("due_date", "must be a date in YYYY-MM-DD format")

def _parse_overdue(overdue: bool | str | None) -> bool | None:
    """Convert an overdue filter value to a bool.

    Args:
        overdue: True, False, "true", "false", or None for no filter.

    Returns:
        True or False, or None if no filter was given.

    Raises:
        ValidationError: If overdue is any other value.
    """
    if overdue is None or isinstance(overdue, bool):
        return overdue
    if overdue == "true":
        return True
    if overdue == "false":
        return False
    raise ValidationError("overdue", "must be true or false")

def _is_overdue(task: dict, today: date) -> bool:
    """Check whether a task is overdue.

    Args:
        task: The task record. A missing or None due_date means no due date.
        today: The date to compare against.

    Returns:
        True if the task is not done and its due date is before today.

    Raises:
        None.
    """
    due_date = task.get("due_date")
    return due_date is not None and not task["done"] and date.fromisoformat(due_date) < today

def archive_task(task_id: int) -> dict:
    """Mark a task as archived.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The updated task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    task = get_task(task_id)
    task["archived"] = True
    return task

def _parse_include_archived(value: bool | str | None) -> bool:
    """Convert an include_archived value to a boolean.

    Args:
        value: True, False, None, or the string "true" or "false", such as a
            raw query-string value. None means False.

    Returns:
        True if archived tasks should be included, otherwise False.

    Raises:
        ValidationError: If value is not True, False, None, "true", or "false".
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value in ("true", "false"):
        return value == "true"
    raise ValidationError("include_archived", "must be true or false")

def list_tasks(
    priority: int | str | None = None,
    *,
    overdue: bool | str | None = None,
    include_archived: bool | str | None = None,
    today: date | None = None,
) -> list[dict]:
    """Retrieve tasks, optionally filtered by priority, overdue status and archived state.

    Archived tasks are left out unless include_archived is true. A task with
    no "archived" key is treated as not archived.

    Args:
        priority: The priority to filter by, from 1 to 5. May be an integer or
            a string of digits such as a raw query-string value. If None, no
            priority filter is applied.
        overdue: Keyword-only. True or "true" returns only overdue tasks
            (due date before today and not done); False or "false" returns
            only tasks that are not overdue. If None, no overdue filter is
            applied.
        include_archived: Keyword-only. Whether to include archived tasks. May
            be True, False, None, or the string "true" or "false". Defaults to
            None, which means False.
        today: Keyword-only. The date used to decide what is overdue.
            Defaults to the current date.

    Returns:
        A list of task records matching every given filter. Empty if none match.

    Raises:
        ValidationError: If priority is not an integer from 1 to 5, overdue
            is not True, False, None, "true", or "false", or include_archived
            is not True, False, None, "true", or "false".
    """
    if isinstance(priority, str):
        if not (priority.isascii() and priority.isdigit()):
            raise ValidationError("priority", "must be an integer between 1 and 5")
        priority = int(priority)
    if priority is not None:
        _validate_priority(priority)
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

def _validate_priority(priority: int) -> None:
    """Check that a priority is an integer from 1 to 5.

    Args:
        priority: The priority value to check.

    Returns:
        None.

    Raises:
        ValidationError: If priority is not an integer from 1 to 5.
    """
    if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
        raise ValidationError("priority", "must be an integer between 1 and 5")

def create_task(
    title: str,
    user_id: int,
    priority: int = DEFAULT_PRIORITY,
    category: str = DEFAULT_CATEGORY,
    tags: list[str] | None = None,
    due_date: str | None = None,
) -> dict:
    """Create a new task.

    Args:
        title: The title of the task. Runs of whitespace are collapsed to a
            single space, leading and trailing whitespace is removed, and the
            first letter is capitalized. The result is what is validated
            and stored.
        user_id: The unique identifier for the user the task belongs to.
        priority: The priority of the task, from 1 to 5. Defaults to 3.
        category: The category of the task, one of "work", "personal", or
            "other". Defaults to "other".
        tags: Optional list of tag strings. Tags are lowercased and duplicates
            are removed, keeping first-seen order. Defaults to no tags.
        due_date: Optional due date as an ISO string "YYYY-MM-DD". Defaults
            to None, meaning no due date.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is not a string, is empty after
            normalizing, or is longer than 200 characters after normalizing,
            priority is not an integer from 1 to 5, category is not one of
            "work", "personal", or "other", tags is not a list of strings,
            there are more than 5 tags after removing duplicates, or due_date
            is not None or a real date in "YYYY-MM-DD" format.
        NotFoundError: If no user exists with the given ID.
    """
    if not isinstance(title, str):
        raise ValidationError("title", "cannot be empty")
    title = " ".join(title.split())
    if not title:
        raise ValidationError("title", "cannot be empty")
    title = title[0].upper() + title[1:]
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError("title", f"must be at most {MAX_TITLE_LENGTH} characters")
    _validate_priority(priority)
    if not isinstance(category, str) or category not in TASK_CATEGORIES:
        raise ValidationError("category", "must be one of: work, personal, other")
    if tags is None:
        tags = []
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        raise ValidationError("tags", "must be a list of strings")
    tags = list(dict.fromkeys(tag.lower() for tag in tags))
    if len(tags) > 5:
        raise ValidationError("tags", "must have at most 5 tags")
    _validate_due_date(due_date)
    get_user(user_id)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {
        "id": new_id,
        "title": title,
        "done": False,
        "user_id": user_id,
        "priority": priority,
        "category": category,
        "tags": tags,
        "due_date": due_date,
    }
    return TASKS[new_id]

def update_task(task_id: int, updates: dict) -> dict:
    """Update a task's priority, title, and/or due date.

    Args:
        task_id: The unique identifier for the task.
        updates: The fields to change. May contain any of "priority", "title",
            and "due_date". A key that is absent leaves that field unchanged.
            A due_date of None clears the due date.

    Returns:
        The updated task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If none of priority, title, or due_date is provided,
            priority is not an integer from 1 to 5, title is empty, or
            due_date is not None or a real date in "YYYY-MM-DD" format.
    """
    task = get_task(task_id)
    if not isinstance(updates, dict) or not any(field in updates for field in _UPDATE_FIELDS):
        raise ValidationError("update", "must include priority or title")
    if "priority" in updates:
        _validate_priority(updates["priority"])
    if "title" in updates:
        title = updates["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("title", "cannot be empty")
    if "due_date" in updates:
        _validate_due_date(updates["due_date"])
    for field in _UPDATE_FIELDS:
        if field in updates:
            task[field] = updates[field]
    return task
