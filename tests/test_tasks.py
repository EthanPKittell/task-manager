import pytest
from app import app
from services.tasks import (
    process_order,
    get_task,
    create_task,
    get_tasks_for_user,
    list_tasks,
    update_task,
)
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
