# ToDoAPP/test/test_admin.py

from fastapi import status

from ..utils import (
    client,
    override_get_db,
    override_get_current_user,
    TestingSessionLocal,
    Todos,
    test_todo,   # fixture
)
from ..routers import admin
from ..main import app

# Ensure admin routes use test DB + fake admin user
app.dependency_overrides[admin.get_db] = override_get_db
app.dependency_overrides[admin.get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    """
    Admin can read all todos
    """
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 1

    todo = data[0]
    assert todo["id"] == test_todo.id
    assert todo["title"] == test_todo.title
    assert todo["description"] == test_todo.description
    assert todo["priority"] == test_todo.priority
    assert todo["complete"] is False
    assert todo["owner_id"] == 1


def test_admin_delete_todo(test_todo):
    """
    Admin can delete an existing todo
    """
    response = client.delete(f"/admin/todo/{test_todo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == test_todo.id).first()
    assert model is None


def test_admin_delete_todo_not_found():
    """
    Admin deleting a non-existent todo returns 404
    """
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo not found."}