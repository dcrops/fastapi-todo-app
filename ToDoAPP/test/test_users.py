from fastapi import status

from ..utils import (
    client,
    override_get_db,
    override_get_current_user,
    test_user
)
from ..routers import users
from ..main import app

# Wire the users router to use the test DB + fake user
app.dependency_overrides[users.get_db] = override_get_db
app.dependency_overrides[users.get_current_user] = override_get_current_user


def test_return_user(test_user):  
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role

def test_change_password_success(test_user):
    response = client.put("/user/password", json={"password": "testpassword", 
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/password", json={"password": "wrong_password", 
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on password change'}

def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/2222222222")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    