from services.users import get_user
from utils.errors import NotFoundError, ValidationError

DEFAULT_PRIORITY = 3

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 1},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 5},
}

def process_order(task_id: int) -> dict:
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

def create_task(title: str, user_id: int, priority: int = DEFAULT_PRIORITY) -> dict:
    """Create a new task.

    Args:
        title: The title of the task.
        user_id: The unique identifier for the user the task belongs to.
        priority: The priority of the task, from 1 to 5. Defaults to 3.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is empty or priority is not an integer from 1 to 5.
        NotFoundError: If no user exists with the given ID.
    """
    if not title or not title.strip():
        raise ValidationError("title", "cannot be empty")
    if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
        raise ValidationError("priority", "must be an integer between 1 and 5")
    get_user(user_id)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {
        "id": new_id,
        "title": title,
        "done": False,
        "user_id": user_id,
        "priority": priority,
    }
    return TASKS[new_id]
