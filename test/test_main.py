from test.utils import *
from fastapi import status



def test_root():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": "Expense Tracker API",
        "version": "1.0.0",
        "description": "REST API for managing personal expenses with JWT authentication"
    }


def test_api_health_check():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == { "status" : "healthy" }