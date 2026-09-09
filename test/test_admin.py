from fastapi import status
from test.utils import *
from routers.admin import get_db

app.dependency_overrides[get_db] = override_get_db


def test_get_all_users(test_user):
    response = client.get("admin/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["username"] == test_user.username
    assert response.json()[0]["email"] == test_user.email
    assert response.json()[0]["role"] == test_user.role


def test_get_user_by_id(test_user):
    response = client.get(f"admin/users/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_user.id
    assert response.json()["username"] == test_user.username
    assert response.json()["email"] == test_user.email
    assert response.json()["role"] == test_user.role


def test_get_user_by_id_not_found(test_user):
    response = client.get("admin/users/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User Not Found"


def test_update_user_role(test_user):
    request_body = {
        "role": "user"
    }
    response = client.patch(
        f"admin/users/{test_user.id}/role",
        json=request_body
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "user"


def test_update_user_role_not_found(test_user):
    request_body = {
        "role": "user"
    }
    response = client.patch(
        "admin/users/999/role",
        json=request_body
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User Not Found"


def test_update_user_role_invalid_role(test_user):
    request_body = {
        "role": "superadmin"
    }
    response = client.patch(
        f"admin/users/{test_user.id}/role",
        json=request_body
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_all_expenses(test_user, test_expense):
    response = client.get("admin/expenses")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["title"] == test_expense.title
    assert response.json()[0]["user_id"] == test_expense.user_id


def test_get_expense_by_id(test_user, test_expense):
    response = client.get(f"admin/expenses/{test_expense.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_expense.id
    assert response.json()["title"] == test_expense.title
    assert response.json()["user_id"] == test_expense.user_id


def test_get_expense_by_id_not_found(test_user):
    response = client.get("admin/expenses/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Expense Not Found"


def test_get_expenses_by_user_id(test_user, test_expense):
    response = client.get(f"admin/expenses/user/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["id"] == test_expense.id
    assert response.json()[0]["user_id"] == test_user.id


def test_get_expenses_by_user_id_user_not_found(test_user):
    response = client.get("admin/expenses/user/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User Not Found"


def test_delete_expense_by_id(test_user, test_expense):
    response = client.delete(f"admin/expenses/{test_expense.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_user(test_user, test_expense):
    response = client.delete(f"admin/users/{test_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
