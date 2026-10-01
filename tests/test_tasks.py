import pytest
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
