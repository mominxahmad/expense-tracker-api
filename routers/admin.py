from fastapi import APIRouter, Depends, HTTPException, Path
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from routers.auth import authenticate_current_user
from starlette import status
from models import User, Expense
from pydantic import BaseModel


router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

database_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(authenticate_current_user)]

def confirm_admin_role(user: user_dependency):
    if user.get("role")=="admin":
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admins Only")

admin_dependency = Annotated[dict, Depends(confirm_admin_role)]


class UserResponseModel(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    role:  str


@router.get("/users", response_model=list[UserResponseModel], status_code=status.HTTP_200_OK)
async def get_all_users(db: database_dependency, admin: admin_dependency):
    users_to_return = db.query(User).all()
    return users_to_return


@router.get("/users/{user_id}", response_model=UserResponseModel, status_code=status.HTTP_200_OK)
async def get_user_by_id(db: database_dependency, admin: admin_dependency, user_id: int = Path(gt=0)):
    user_to_return = db.query(User).filter(User.id==user_id).first()
    if user_to_return is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
    return user_to_return


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(db: database_dependency, admin: admin_dependency, user_id: int = Path(gt=0)):
    user_to_delete = db.query(User).filter(User.id==user_id).first()
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found")
    expenses_to_delete = db.query(Expense).filter(Expense.user_id==user_id).all()
    for expense in expenses_to_delete:
        db.delete(expense)
    db.delete(user_to_delete)
    db.commit()

