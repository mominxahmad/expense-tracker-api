from test.utils import *
from routers.expenses import get_db, authenticate_current_user
from fastapi import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[authenticate_current_user] = override_authenticate_current_user


def test_get_all_expenses(test_expense):
    response = client.get("/expenses/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "id" : 1,
        "title" : "gym membership",
        "amount" : 5000,
        "category" : "subscriptions",
        "description" : "Uni sept membership fee for the gym",
        "user_id" : 1
    }]


def test_get_expense_by_id(test_expense):
    response = client.get("/expenses/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id" : 1,
        "title" : "gym membership",
        "amount" : 5000,
        "category" : "subscriptions",
        "description" : "Uni sept membership fee for the gym",
        "user_id" : 1
    }
def test_get_expense_by_INVALID_id(test_expense):
    response = client.get("/expenses/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { "detail" : "Expense Not Found" }

def test_create_new_expense():
    request_data = {
        "title" : "test expense",
        "amount" : 3456,
        "category" : "food",
        "description": ""
    }
    response = client.post("/expenses/",json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id" : 1,
        "title" : "test expense",
        "amount" : 3456,
        "category" : "food",
        "description" : "",
        "user_id" : 1
    }


def test_update_expense_by_id(test_expense):
    request_data = {
        "title": "updated expense",
        "amount": 3000,
        "category": "hello",
        "description": "lorem ipsum delor"
    }
    response = client.put("/expenses/1",json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_update_expense_by_INVALID_id(test_expense):
    request_data = {
        "title": "updated expense",
        "amount": 3000,
        "category": "hello",
        "description": "lorem ipsum delor"
    }
    response = client.put("/expenses/99", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND