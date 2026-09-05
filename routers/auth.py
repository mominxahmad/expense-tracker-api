from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import User
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Authorization"])


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


@router.post("/register",status_code=status.HTTP_201_CREATED)
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
