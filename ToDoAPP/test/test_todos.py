# ToDoAPP/test/test_todos.py

from fastapi import status

from ..utils import (
    client,
    override_get_db,
    override_get_current_user,
    TestingSessionLocal,
    Todos,
    test_todo
)
from ..routers import todos
from ..main import app

# Wire the todos router to use the test DB + fake user
app.dependency_overrides[todos.get_db] = override_get_db
app.dependency_overrides[todos.get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "complete": False,
            "title": "Learn to code",
            "description": "Need to learn everyday!",
            "id": test_todo.id,
            "priority": 5,
            "owner_id": 1,
        }
    ]


def test_read_one_authenticated(test_todo):
    response = client.get(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "complete": False,
        "title": "Learn to code",
        "description": "Need to learn everyday!",
        "id": test_todo.id,
        "priority": 5,
        "owner_id": 1,
    }


def test_read_one_authenticated_not_foun():
    response = client.get("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}


def test_create_todo(test_todo):
    request_data = {
        "title": "New Todo!",
        "description": "New todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/todos/todo/", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == test_todo.id + 1).first()
    assert model.title == request_data["title"]
    assert model.description == request_data["description"]
    assert model.priority == request_data["priority"]
    assert model.complete == request_data["complete"]


def test_update_todo(test_todo):
    request_data = {
        "title": "Change the title of the todo already saved!",
        "description": "New todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.put(f"/todos/todo/{test_todo.id}", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model.title == request_data["title"]


def test_update_todo_not_found():
    request_data = {
        "title": "Change the title of the todo already saved!",
        "description": "New todo description",
        "priority": 5,
        "complete": False,
    }

    response = client.put("/todos/todo/999", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}


def test_delete_todo(test_todo):
    response = client.delete(f"/todos/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete("/todos/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}