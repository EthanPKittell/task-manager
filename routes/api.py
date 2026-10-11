from flask import Blueprint, Response, jsonify, request
from services.tasks import DEFAULT_PRIORITY, get_task, create_task, list_tasks, process_order, update_task
from services.users import get_notification_pref, get_user, list_users, update_notification_pref
from utils.errors import AppError

api = Blueprint("api", __name__)

@api.errorhandler(AppError)
def handle_app_error(e):
    return jsonify({"error": e.message}), e.status_code

@api.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_route(task_id):
    return jsonify(get_task(task_id))

@api.route("/tasks", methods=["GET"])
def list_tasks_route() -> Response:
    """List all tasks, optionally filtered by the priority query parameter.

    Args:
        None.

    Returns:
        A JSON response containing a list of task records.

    Raises:
        ValidationError: If the priority query parameter is not an integer
            from 1 to 5.
    """
    return jsonify(list_tasks(request.args.get("priority")))

@api.route("/tasks", methods=["POST"])
def create_task_route():
    data = request.get_json()
    priority = data.get("priority", DEFAULT_PRIORITY)
    return jsonify(create_task(data["title"], data["user_id"], priority)), 201

@api.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task_route(task_id: int) -> Response:
    """Update a task's priority and/or title from the JSON request body.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        A JSON response containing the updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If the body has neither priority nor title, or either
            value is invalid.
    """
    return jsonify(update_task(task_id, request.get_json()))

@api.route("/users", methods=["GET"])
def list_users_route() -> Response:
    """List all users.

    Args:
        None.

    Returns:
        A JSON response containing a list of user records.

    Raises:
        None.
    """
    return jsonify(list_users())

@api.route("/users/<int:user_id>", methods=["GET"])
def get_user_route(user_id):
    return jsonify(get_user(user_id))

@api.route("/users/<int:user_id>/notifications", methods=["GET"])
def get_notification_pref_route(user_id: int) -> Response:
    """Retrieve a user's notification preference.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A JSON response containing the user ID and notification preference.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    return jsonify({"user_id": user_id, "notification_pref": get_notification_pref(user_id)})

@api.route("/users/<int:user_id>/notifications", methods=["PATCH"])
def update_notification_pref_route(user_id: int) -> Response:
    """Update a user's notification preference from the JSON request body.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A JSON response containing the user ID and updated notification
        preference.

    Raises:
        NotFoundError: If no user exists with the given ID.
        ValidationError: If notification_pref is missing or is not one of
            "email", "sms", or "none".
    """
    user = update_notification_pref(user_id, request.get_json().get("notification_pref"))
    return jsonify({"user_id": user["id"], "notification_pref": user["notification_pref"]})
