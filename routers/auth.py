from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone , timedelta
from jose import jwt
import os
from dotenv import load_dotenv


router = APIRouter(prefix="/auth", tags=["Authorization"])


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

database_dependency = Annotated[Session,Depends(get_db)]


class CreateUserModel(BaseModel):
    email: str = Field(description="User's Email address", examples=["johndoe@email.com"] , pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    username: str = Field(description="User's Username", examples=["johndoe"], min_length=4,max_length=20)
    first_name: str = Field(description="User's First Name", examples=["John"], min_length=4,max_length=20)
    last_name: str = Field(description="User's Last Name", examples=["Doe"], min_length=4,max_length=20)
    password: str = Field(description="Password with 6+ characters", min_length=6)


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


Oauth_dependency=Annotated[OAuth2PasswordRequestForm, Depends()]


def confirm_and_get_user(username: str, plain_password: str, db: Session):
    user = db.query(User).filter(User.username==username).first()
    if user is None:
        return False
    if not bcrypt_context.verify(plain_password, user.hashed_password):
        return False
    return user


def assign_token(id: int, username: str, role: str, time_delta: timedelta):
    encode = {
        "sub": username,
        "id": id,
        "role": role
    }
    expires = datetime.now(timezone.utc) + time_delta
    encode.update({"exp":expires})
    return jwt.encode(encode,SECRET_KEY,ALGORITHM)


class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(db: database_dependency, user_data: CreateUserModel):
    new_user = User(
        email = user_data.email,
        username = user_data.username,
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        hashed_password = bcrypt_context.hash(user_data.password)
    )
    db.add(new_user)
    db.commit()


@router.post("/login", response_model=Token)
async def login_for_access_token(db: database_dependency, form_data: Oauth_dependency):
    user = confirm_and_get_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = assign_token(user.id, user.username, user.role, timedelta(minutes=30))
    return {
        "access_token": token,
        "token_type": "bearer"
    }