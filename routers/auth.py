from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timezone , timedelta
from jose import jwt, JWTError
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
    username: str = Field(description="User's Username", examples=["johndoe"], min_length=3,max_length=20)
    first_name: str = Field(description="User's First Name", examples=["John"], min_length=3,max_length=20)
    last_name: str = Field(description="User's Last Name", examples=["Doe"], min_length=3,max_length=20)
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

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
async def authenticate_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id = payload.get("id")
        username = payload.get("sub")
        role = payload.get("role")
        if id is None or username is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User Verification Failed")
        return {
            "id": id,
            "username": username,
            "role": role
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User Verification Failed")



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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Credentials")
    token = assign_token(user.id, user.username, user.role, timedelta(minutes=30))
    return {
        "access_token": token,
        "token_type": "bearer"
    }