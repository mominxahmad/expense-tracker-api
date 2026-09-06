from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from routers.auth import authenticate_current_user
from starlette import status


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
