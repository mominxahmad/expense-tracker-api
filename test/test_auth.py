from fastapi import status, HTTPException
from test.utils import  *
from routers.auth import get_db, confirm_and_get_user,assign_token,SECRET_KEY,ALGORITHM,authenticate_current_user
from datetime import timedelta
from jose import jwt
import pytest


app.dependency_overrides[get_db] = override_get_db


def test_create_user():
    request_body = {
        "email":"test@email.com",
        "username":"test_user",
        "first_name": "f_test",
        "last_name": "l_test",
        "password": "hello123"
    }
    response = client.post("auth/register",json=request_body)
    assert response.status_code == status.HTTP_201_CREATED


def test_confirm_and_get_user(test_user):
    username = "test_user"
    password = "testing123"
    db = TestingSessionLocal()
    check = confirm_and_get_user(username,password,db )
    assert check.id == 1
    assert check.email == "test@email.com"
    assert check.username == "test_user"
    assert check.first_name == "f_test"
    assert check.last_name == "l_test"
    assert check.role == "admin"


def test_assign_token():
    time_delta = timedelta(minutes=20)
    id = 1
    username = "test_user"
    role = "admin"
    token =  assign_token(id, username, role, time_delta)
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    assert payload.get("id") == 1
    assert payload.get("sub") == "test_user"
    assert payload.get("role") == "admin"


@pytest.mark.asyncio
async def test_authenticate_current_user():
    encode = {"sub":"test_user","id":1,"role":"admin"}
    token = jwt.encode(encode,SECRET_KEY,ALGORITHM)
    decoded_token =  await authenticate_current_user(token)
    assert decoded_token == {
            "id": 1,
            "username": "test_user",
            "role": "admin"
        }


@pytest.mark.asyncio
async def test_authenticate_current_user_FAILURE():
    encode = {'role': "admin"}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await authenticate_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "User Verification Failed"
