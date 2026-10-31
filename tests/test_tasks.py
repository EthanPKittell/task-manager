import pytest
from app import app
from services.tasks import (
    DEFAULT_PRIORITY,
    process_order,
    get_task,
    create_task,
    get_tasks_by_status,
    get_tasks_for_user,
    list_tasks,
    update_task,
)
from services.users import (
    NOTIFICATION_PREFS,
    create_user,
    get_notification_pref,
    get_user,
    list_users,
    update_notification_pref,
)
from services.tags import create_tag
from utils.errors import NotFoundError, ValidationError

def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(Exception):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(Exception):
        get_task(999)

def test_create_task_valid():
    result = create_task("Water plants", 1)
    assert result["title"] == "Water plants"
    assert result["done"] is False
    assert result["user_id"] == 1
    assert get_task(result["id"]) == result

def test_create_task_empty_title():
    with pytest.raises(ValidationError):
        create_task("   ", 1)

def test_create_task_unknown_user():
    with pytest.raises(NotFoundError):
        create_task("Water plants", 999)

def test_get_tasks_for_user_valid():
    result = get_tasks_for_user(2)
    assert [task["id"] for task in result] == [3]
    assert all(task["user_id"] == 2 for task in result)

def test_get_tasks_for_user_unknown_user():
    with pytest.raises(NotFoundError):
        get_tasks_for_user(999)

def test_seed_tasks_have_priority():
    assert get_task(1)["priority"] == 1
    assert get_task(2)["priority"] == 3
    assert get_task(3)["priority"] == 5

def test_create_task_default_priority():
    result = create_task("Water plants", 1)
    assert result["priority"] == 3

def test_create_task_with_priority():
    result = create_task("Water plants", 1, 5)
    assert result["priority"] == 5
    assert get_task(result["id"])["priority"] == 5

@pytest.mark.parametrize("priority", [0, 6, -1, "high", 2.5, True, None])
def test_create_task_invalid_priority(priority):
    with pytest.raises(ValidationError):
        create_task("Water plants", 1, priority)

def test_create_task_route_with_priority():
    response = app.test_client().post(
        "/api/tasks", json={"title": "Water plants", "user_id": 1, "priority": 1}
    )
    assert response.status_code == 201
    assert response.get_json()["priority"] == 1

def test_create_task_route_default_priority():
    response = app.test_client().post(
        "/api/tasks", json={"title": "Water plants", "user_id": 1}
    )
    assert response.status_code == 201
    assert response.get_json()["priority"] == 3

def test_create_task_route_invalid_priority():
    response = app.test_client().post(
        "/api/tasks", json={"title": "Water plants", "user_id": 1, "priority": 9}
    )
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_update_task_priority_only():
    task_id = create_task("Water plants", 1, 2)["id"]
    result = update_task(task_id, {"priority": 5})
    assert result["priority"] == 5
    assert result["title"] == "Water plants"
    assert get_task(task_id) == result

def test_update_task_title_only():
    task_id = create_task("Water plants", 1, 2)["id"]
    result = update_task(task_id, {"title": "Feed cat"})
    assert result["title"] == "Feed cat"
    assert result["priority"] == 2
    assert get_task(task_id) == result

def test_update_task_priority_and_title():
    task_id = create_task("Water plants", 1, 2)["id"]
    result = update_task(task_id, {"priority": 4, "title": "Feed cat"})
    assert result["priority"] == 4
    assert result["title"] == "Feed cat"

def test_update_task_unknown_task():
    with pytest.raises(NotFoundError):
        update_task(999, {"priority": 1})

def test_update_task_no_fields():
    task_id = create_task("Water plants", 1)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {})

@pytest.mark.parametrize("priority", [0, 6, -1, "high", 2.5, True, None])
def test_update_task_invalid_priority(priority):
    task_id = create_task("Water plants", 1)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {"priority": priority})

@pytest.mark.parametrize("title", ["", "   ", 123, None])
def test_update_task_invalid_title(title):
    task_id = create_task("Water plants", 1)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {"title": title})

def test_update_task_no_partial_update():
    task_id = create_task("Water plants", 1, 2)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {"priority": 5, "title": "   "})
    assert get_task(task_id)["priority"] == 2
    assert get_task(task_id)["title"] == "Water plants"

def test_update_task_route_priority_only():
    task_id = create_task("Water plants", 1, 2)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={"priority": 5})
    assert response.status_code == 200
    assert response.get_json()["priority"] == 5
    assert response.get_json()["title"] == "Water plants"

def test_update_task_route_title_only():
    task_id = create_task("Water plants", 1, 2)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={"title": "Feed cat"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Feed cat"
    assert response.get_json()["priority"] == 2

def test_update_task_route_priority_and_title():
    task_id = create_task("Water plants", 1, 2)["id"]
    response = app.test_client().patch(
        f"/api/tasks/{task_id}", json={"priority": 4, "title": "Feed cat"}
    )
    assert response.status_code == 200
    assert response.get_json()["priority"] == 4
    assert response.get_json()["title"] == "Feed cat"

def test_update_task_route_unknown_task():
    response = app.test_client().patch("/api/tasks/999", json={"priority": 1})
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_update_task_route_invalid_priority():
    task_id = create_task("Water plants", 1)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={"priority": 9})
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_update_task_route_null_priority():
    task_id = create_task("Water plants", 1, 2)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={"priority": None})
    assert response.status_code == 422
    assert "error" in response.get_json()
    assert get_task(task_id)["priority"] == 2

def test_update_task_route_neither_field():
    task_id = create_task("Water plants", 1)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={})
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_list_tasks_all():
    result = list_tasks()
    assert {1, 2, 3} <= {task["id"] for task in result}

def test_list_tasks_filter_by_priority():
    result = list_tasks(5)
    ids = [task["id"] for task in result]
    assert all(task["priority"] == 5 for task in result)
    assert 3 in ids
    assert 1 not in ids

def test_list_tasks_string_priority():
    assert list_tasks("5") == list_tasks(5)

@pytest.mark.parametrize("priority", [0, 6, -1, "high", "2.5", "", "0", "6", 2.5, True])
def test_list_tasks_invalid_priority(priority):
    with pytest.raises(ValidationError):
        list_tasks(priority)

def test_list_tasks_route_all():
    response = app.test_client().get("/api/tasks")
    assert response.status_code == 200
    assert {1, 2, 3} <= {task["id"] for task in response.get_json()}

def test_list_tasks_route_filter_by_priority():
    response = app.test_client().get("/api/tasks?priority=1")
    assert response.status_code == 200
    result = response.get_json()
    assert all(task["priority"] == 1 for task in result)
    assert 1 in [task["id"] for task in result]

@pytest.mark.parametrize("priority", ["9", "abc", ""])
def test_list_tasks_route_invalid_priority(priority):
    response = app.test_client().get(f"/api/tasks?priority={priority}")
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_create_task_default_priority_matches_constant() -> None:
    result = create_task("Water plants", 1)
    assert DEFAULT_PRIORITY == 3
    assert result["priority"] == DEFAULT_PRIORITY
    assert get_task(result["id"])["priority"] == DEFAULT_PRIORITY

def test_create_task_default_priority_is_filterable() -> None:
    task_id = create_task("Water plants", 1)["id"]
    assert task_id in [task["id"] for task in list_tasks(3)]
    assert task_id not in [task["id"] for task in list_tasks(1)]

@pytest.mark.parametrize("priority", [0, 6, "3", 5.0])
def test_create_task_invalid_priority_creates_nothing(priority) -> None:
    count = len(list_tasks())
    with pytest.raises(ValidationError):
        create_task("Water plants", 1, priority)
    assert len(list_tasks()) == count

def test_create_task_invalid_priority_message() -> None:
    with pytest.raises(ValidationError) as exc_info:
        create_task("Water plants", 1, 9)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid priority: must be an integer between 1 and 5"

@pytest.mark.parametrize("priority", [0, 6, "high", "3", 2.5, True, None])
def test_create_task_route_invalid_priority_types(priority) -> None:
    response = app.test_client().post(
        "/api/tasks", json={"title": "Water plants", "user_id": 1, "priority": priority}
    )
    assert response.status_code == 422
    assert "error" in response.get_json()

@pytest.mark.parametrize("priority", [0, 6, "3", 5.0])
def test_update_task_invalid_priority_leaves_task_unchanged(priority) -> None:
    task_id = create_task("Water plants", 1, 2)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {"priority": priority})
    assert get_task(task_id)["priority"] == 2
    assert get_task(task_id)["title"] == "Water plants"

def test_update_task_invalid_priority_with_valid_title_no_partial_update() -> None:
    task_id = create_task("Water plants", 1, 2)["id"]
    with pytest.raises(ValidationError):
        update_task(task_id, {"priority": 9, "title": "Feed cat"})
    assert get_task(task_id)["priority"] == 2
    assert get_task(task_id)["title"] == "Water plants"

@pytest.mark.parametrize("priority", [0, 6, "high", "3", 2.5, True])
def test_update_task_route_invalid_priority_types(priority) -> None:
    task_id = create_task("Water plants", 1, 2)["id"]
    response = app.test_client().patch(f"/api/tasks/{task_id}", json={"priority": priority})
    assert response.status_code == 422
    assert "error" in response.get_json()
    assert get_task(task_id)["priority"] == 2

@pytest.mark.parametrize("priority", [1, 2, 3, 4, 5])
def test_list_tasks_filter_each_valid_priority(priority) -> None:
    task_id = create_task("Water plants", 1, priority)["id"]
    result = list_tasks(priority)
    assert all(task["priority"] == priority for task in result)
    assert task_id in [task["id"] for task in result]

def test_list_tasks_filter_excludes_other_priorities() -> None:
    low_id = create_task("Water plants", 1, 2)["id"]
    high_id = create_task("Feed cat", 1, 4)["id"]
    low_ids = [task["id"] for task in list_tasks(2)]
    high_ids = [task["id"] for task in list_tasks(4)]
    assert low_id in low_ids
    assert high_id not in low_ids
    assert high_id in high_ids
    assert low_id not in high_ids

def test_list_tasks_filter_reflects_priority_update() -> None:
    task_id = create_task("Water plants", 1, 2)["id"]
    update_task(task_id, {"priority": 4})
    assert task_id not in [task["id"] for task in list_tasks(2)]
    assert task_id in [task["id"] for task in list_tasks(4)]

def test_list_tasks_route_filter_matches_service() -> None:
    task_id = create_task("Water plants", 1, 5)["id"]
    response = app.test_client().get("/api/tasks?priority=5")
    assert response.status_code == 200
    ids = [task["id"] for task in response.get_json()]
    assert task_id in ids
    assert ids == [task["id"] for task in list_tasks(5)]

def test_seed_users_default_notification_pref() -> None:
    assert get_user(1)["notification_pref"] == "none"
    assert get_user(2)["notification_pref"] == "none"

def test_create_user_default_notification_pref() -> None:
    result = create_user("Carol", "carol@example.com")
    assert result["notification_pref"] == "none"
    assert get_user(result["id"])["notification_pref"] == "none"
    assert get_notification_pref(result["id"]) == "none"

def test_get_notification_pref_seed_user() -> None:
    assert get_notification_pref(1) == "none"

@pytest.mark.parametrize("pref", ["email", "sms", "none"])
def test_update_notification_pref_valid(pref) -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    result = update_notification_pref(user_id, pref)
    assert result["id"] == user_id
    assert result["notification_pref"] == pref
    assert get_notification_pref(user_id) == pref
    assert get_user(user_id) == result

def test_update_notification_pref_leaves_other_users_unchanged() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    other_id = create_user("Dave", "dave@example.com")["id"]
    update_notification_pref(user_id, "email")
    assert get_notification_pref(user_id) == "email"
    assert get_notification_pref(other_id) == "none"

@pytest.mark.parametrize("pref", ["push", "", "EMAIL", None, 1])
def test_update_notification_pref_invalid(pref) -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "sms")
    with pytest.raises(ValidationError):
        update_notification_pref(user_id, pref)
    assert get_notification_pref(user_id) == "sms"

def test_update_notification_pref_invalid_message() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    with pytest.raises(ValidationError) as exc_info:
        update_notification_pref(user_id, "push")
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid notification_pref: must be one of: email, sms, none"

def test_get_notification_pref_unknown_user() -> None:
    with pytest.raises(NotFoundError):
        get_notification_pref(999)

def test_update_notification_pref_unknown_user() -> None:
    with pytest.raises(NotFoundError):
        update_notification_pref(999, "email")

def test_list_users_includes_notification_pref() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "email")
    result = list_users()
    assert {1, 2, user_id} <= {user["id"] for user in result}
    assert all(user["notification_pref"] in NOTIFICATION_PREFS for user in result)
    assert {"id": user_id, "name": "Carol", "email": "carol@example.com", "notification_pref": "email"} in result

def test_list_users_route() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "sms")
    response = app.test_client().get("/api/users")
    assert response.status_code == 200
    result = response.get_json()
    assert {1, 2, user_id} <= {user["id"] for user in result}
    assert all(user["notification_pref"] in NOTIFICATION_PREFS for user in result)
    assert [user["notification_pref"] for user in result if user["id"] == user_id] == ["sms"]

def test_get_user_route_includes_notification_pref() -> None:
    response = app.test_client().get("/api/users/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1
    assert response.get_json()["notification_pref"] == "none"

def test_get_user_route_reflects_updated_notification_pref() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "email")
    response = app.test_client().get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert response.get_json()["notification_pref"] == "email"

def test_get_notification_pref_route() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    response = app.test_client().get(f"/api/users/{user_id}/notifications")
    assert response.status_code == 200
    assert response.get_json() == {"user_id": user_id, "notification_pref": "none"}

def test_get_notification_pref_route_unknown_user() -> None:
    response = app.test_client().get("/api/users/999/notifications")
    assert response.status_code == 404
    assert "error" in response.get_json()

@pytest.mark.parametrize("pref", ["email", "sms", "none"])
def test_update_notification_pref_route_valid(pref) -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    response = app.test_client().patch(
        f"/api/users/{user_id}/notifications", json={"notification_pref": pref}
    )
    assert response.status_code == 200
    assert response.get_json() == {"user_id": user_id, "notification_pref": pref}
    assert get_notification_pref(user_id) == pref

@pytest.mark.parametrize("pref", ["push", "", "EMAIL", None, 1])
def test_update_notification_pref_route_invalid(pref) -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "sms")
    response = app.test_client().patch(
        f"/api/users/{user_id}/notifications", json={"notification_pref": pref}
    )
    assert response.status_code == 422
    assert "error" in response.get_json()
    assert get_notification_pref(user_id) == "sms"

def test_update_notification_pref_route_missing_value() -> None:
    user_id = create_user("Carol", "carol@example.com")["id"]
    update_notification_pref(user_id, "sms")
    response = app.test_client().patch(f"/api/users/{user_id}/notifications", json={})
    assert response.status_code == 422
    assert "error" in response.get_json()
    assert get_notification_pref(user_id) == "sms"

def test_update_notification_pref_route_unknown_user() -> None:
    response = app.test_client().patch(
        "/api/users/999/notifications", json={"notification_pref": "email"}
    )
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_process_order_unknown_task_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        process_order(999)

def test_create_task_non_string_title_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        create_task(123, 1)

def test_get_tasks_by_status_done() -> None:
    done_id = process_order(create_task("Water plants", 1)["id"])["id"]
    pending_id = create_task("Feed cat", 1)["id"]
    ids = [task["id"] for task in get_tasks_by_status("done")]
    assert all(task["done"] is True for task in get_tasks_by_status("done"))
    assert done_id in ids
    assert 3 in ids
    assert pending_id not in ids

def test_get_tasks_by_status_pending() -> None:
    done_id = process_order(create_task("Water plants", 1)["id"])["id"]
    pending_id = create_task("Feed cat", 1)["id"]
    ids = [task["id"] for task in get_tasks_by_status("pending")]
    assert all(task["done"] is False for task in get_tasks_by_status("pending"))
    assert pending_id in ids
    assert done_id not in ids

def test_get_tasks_by_status_covers_all_tasks() -> None:
    done = get_tasks_by_status("done")
    pending = get_tasks_by_status("pending")
    assert len(done) + len(pending) == len(list_tasks())

@pytest.mark.parametrize("status", ["DONE", "complete", "", None, True, 1])
def test_get_tasks_by_status_invalid(status) -> None:
    with pytest.raises(ValidationError) as exc_info:
        get_tasks_by_status(status)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid status: must be one of: done, pending"

def test_create_tag_valid() -> None:
    result = create_tag({"name": "errands"})
    assert result["name"] == "errands"
    assert isinstance(result["id"], int)
    assert create_tag({"name": "work"})["id"] == result["id"] + 1

@pytest.mark.parametrize("data", [[], "errands", None, 1, {}, {"name": ""}, {"name": "   "}, {"name": 123}, {"name": None}])
def test_create_tag_invalid(data) -> None:
    with pytest.raises(ValidationError) as exc_info:
        create_tag(data)
    assert exc_info.value.status_code == 422

def test_create_tag_invalid_message() -> None:
    with pytest.raises(ValidationError) as exc_info:
        create_tag({"name": "   "})
    assert exc_info.value.message == "Invalid name: cannot be empty"

def test_create_tag_route_valid() -> None:
    response = app.test_client().post("/api/tags", json={"name": "errands"})
    assert response.status_code == 201
    body = response.get_json()
    assert body["name"] == "errands"
    assert isinstance(body["id"], int)

def test_create_tag_route_non_object_body() -> None:
    response = app.test_client().post("/api/tags", json=[])
    assert response.status_code == 422
    assert "error" in response.get_json()

@pytest.mark.parametrize("body", [{}, {"name": ""}, {"name": 123}])
def test_create_tag_route_invalid_name(body) -> None:
    response = app.test_client().post("/api/tags", json=body)
    assert response.status_code == 422
    assert "error" in response.get_json()

def test_get_task_unknown_task_raises_not_found() -> None:
    with pytest.raises(NotFoundError) as exc_info:
        get_task(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "Task not found"

def test_get_user_unknown_user_raises_not_found() -> None:
    with pytest.raises(NotFoundError) as exc_info:
        get_user(999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.message == "User not found"

@pytest.mark.parametrize("name", ["", "   "])
def test_create_user_empty_name_raises_validation_error(name) -> None:
    count = len(list_users())
    with pytest.raises(ValidationError) as exc_info:
        create_user(name, "carol@example.com")
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid name: cannot be empty"
    assert len(list_users()) == count

@pytest.mark.parametrize("email", ["", "carol.example.com"])
def test_create_user_invalid_email_raises_validation_error(email) -> None:
    count = len(list_users())
    with pytest.raises(ValidationError) as exc_info:
        create_user("Carol", email)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid email: must be a valid email address"
    assert len(list_users()) == count

def test_create_task_default_category() -> None:
    result = create_task("Water plants", 1)
    assert result["category"] == "other"
    assert get_task(result["id"])["category"] == "other"

@pytest.mark.parametrize("category", ["work", "personal", "other"])
def test_create_task_with_category(category) -> None:
    result = create_task("Water plants", 1, category=category)
    assert result["category"] == category
    assert get_task(result["id"])["category"] == category

def test_create_task_with_priority_and_category() -> None:
    result = create_task("Water plants", 1, 5, "work")
    assert result["priority"] == 5
    assert result["category"] == "work"

@pytest.mark.parametrize("category", ["home", "", "WORK", " work", None, 1, True])
def test_create_task_invalid_category(category) -> None:
    count = len(list_tasks())
    with pytest.raises(ValidationError) as exc_info:
        create_task("Water plants", 1, category=category)
    assert exc_info.value.status_code == 422
    assert exc_info.value.message == "Invalid category: must be one of: work, personal, other"
    assert len(list_tasks()) == count
