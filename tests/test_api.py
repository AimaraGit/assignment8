"""Unit tests for Task Manager REST API."""

import pytest
from app.main import app, tasks


@pytest.fixture(autouse=True)
def clear_tasks():
    """Reset task store before every test."""
    tasks.clear()
    import app.main as m
    m._next_id = 1
    yield


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# Health
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# Create task
def test_create_task_success(client):
    r = client.post("/tasks", json={"title": "Write tests"})
    assert r.status_code == 201
    data = r.get_json()
    assert data["title"] == "Write tests"
    assert data["done"] is False
    assert data["id"] == 1


def test_create_task_empty_title(client):
    r = client.post("/tasks", json={"title": ""})
    assert r.status_code == 400


def test_create_task_missing_title(client):
    r = client.post("/tasks", json={})
    assert r.status_code == 400


def test_create_task_xss_title(client):
    r = client.post("/tasks", json={"title": "<script>alert(1)</script>"})
    assert r.status_code == 400


def test_create_task_too_long(client):
    r = client.post("/tasks", json={"title": "a" * 201})
    assert r.status_code == 400


# List tasks
def test_list_tasks_empty(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.get_json() == []


def test_list_tasks_returns_created(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})
    r = client.get("/tasks")
    assert len(r.get_json()) == 2


def test_list_tasks_filter_done(client):
    client.post("/tasks", json={"title": "Task A"})
    r = client.get("/tasks?done=false")
    assert len(r.get_json()) == 1


# Delete task
def test_delete_task_success(client):
    client.post("/tasks", json={"title": "Delete me"})
    r = client.delete("/tasks/1", headers={"X-User-Role": "admin"})
    assert r.status_code == 200


def test_delete_task_forbidden(client):
    client.post("/tasks", json={"title": "Delete me"})
    r = client.delete("/tasks/1")
    assert r.status_code == 403


def test_delete_task_not_found(client):
    r = client.delete("/tasks/999", headers={"X-User-Role": "admin"})
    assert r.status_code == 404