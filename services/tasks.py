from services.users import get_user
from utils.errors import NotFoundError, ValidationError

DEFAULT_PRIORITY = 3
TASK_CATEGORIES = ("work", "personal", "other")
DEFAULT_CATEGORY = "other"
MAX_TITLE_LENGTH = 200

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
    include_archived: bool | str | None = None,
) -> list[dict]:
    """Retrieve all tasks, optionally filtered by priority.

    Archived tasks are left out unless include_archived is true. A task with
    no "archived" key is treated as not archived.

    Args:
        priority: The priority to filter by, from 1 to 5. May be an integer or
            a string of digits such as a raw query-string value. If None, tasks
            of every priority are returned.
        include_archived: Keyword-only. Whether to include archived tasks. May
            be True, False, None, or the string "true" or "false". Defaults to
            None, which means False.

    Returns:
        A list of task records. Empty if no tasks match.

    Raises:
        ValidationError: If priority is not an integer from 1 to 5, or
            include_archived is not True, False, None, "true", or "false".
    """
    include_archived = _parse_include_archived(include_archived)
    if priority is not None:
        if isinstance(priority, str):
            if not (priority.isascii() and priority.isdigit()):
                raise ValidationError("priority", "must be an integer between 1 and 5")
            priority = int(priority)
        _validate_priority(priority)
    return [
        task
        for task in TASKS.values()
        if (include_archived or not task.get("archived", False))
        and (priority is None or task["priority"] == priority)
    ]

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

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is not a string, is empty after
            normalizing, or is longer than 200 characters after normalizing,
            priority is not an integer from 1 to 5, category is not one of
            "work", "personal", or "other", tags is not a list of strings,
            or there are more than 5 tags after removing duplicates.
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
    }
    return TASKS[new_id]

def update_task(task_id: int, updates: dict) -> dict:
    """Update a task's priority and/or title.

    Args:
        task_id: The unique identifier for the task.
        updates: The fields to change. May contain "priority", "title", or both.
            A key that is absent leaves that field unchanged.

    Returns:
        The updated task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If neither priority nor title is provided, priority is
            not an integer from 1 to 5, or title is empty.
    """
    task = get_task(task_id)
    if not isinstance(updates, dict) or not ("priority" in updates or "title" in updates):
        raise ValidationError("update", "must include priority or title")
    if "priority" in updates:
        _validate_priority(updates["priority"])
    if "title" in updates:
        title = updates["title"]
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("title", "cannot be empty")
    if "priority" in updates:
        task["priority"] = updates["priority"]
    if "title" in updates:
        task["title"] = updates["title"]
    return task
