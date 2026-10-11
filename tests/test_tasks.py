import pytest
from app import app
from services.tasks import process_order, get_task, create_task, get_tasks_for_user
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
