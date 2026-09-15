from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Field
from database import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from routers.auth import authenticate_current_user
from models import Expense,User
from starlette import status
from sqlalchemy import select


router = APIRouter(prefix="/expenses", tags=["Expenses"])


database_dependency = Annotated[AsyncSession, Depends(get_db)]

user_dependency = Annotated[dict, Depends(authenticate_current_user)]


class CreateExpenseModel(BaseModel):
    title: str = Field(min_length=3, max_length=50, examples=["Task Title"])
    amount: int = Field(examples=[500])
    category: str = Field(min_length=3, max_length=50, examples=["Food"])
    description: str  | None = Field(default=None, max_length=200, examples=["Task Description"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_expenses(db: database_dependency, user: user_dependency):
    response = await db.execute(
        select(Expense).where(Expense.user_id==user.get("id"))
    )
    return response.scalars().all()


@router.get("/{expense_id}", status_code=status.HTTP_200_OK)
async def get_expense_by_id(db: database_dependency, user: user_dependency, expense_id: int = Path(gt=0)):
    response = await db.execute(
        select(Expense).where(Expense.user_id==user.get("id"),
                              Expense.id==expense_id)
    )
    expense_to_return = response.scalar_one_or_none()
    if expense_to_return is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense Not Found")
    return expense_to_return


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_expense(db: database_dependency, user: user_dependency, new_expense: CreateExpenseModel):
    new_expense_model = Expense(**new_expense.model_dump(),user_id=user.get("id"))
    db.add(new_expense_model)
    await db.commit()
    await db.refresh(new_expense_model)
    return new_expense_model


@router.put("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_expense_by_id(db: database_dependency, user: user_dependency, update_model: CreateExpenseModel, expense_id: int = Path(gt=0)):
    response = await db.execute(
        select(Expense).where(Expense.id==expense_id,
                              Expense.user_id==user.get("id"))
    )
    task_to_update = response.scalar_one_or_none()
    if task_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense Not Found")
    task_to_update.title = update_model.title
    task_to_update.category = update_model.category
    task_to_update.amount = update_model.amount
    task_to_update.description = update_model.description
    db.add(task_to_update)
    await db.commit()


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_by_id(db: database_dependency, user: user_dependency, expense_id: int = Path(gt=0)):
    response = await db.execute(
        select(Expense).where(Expense.id==expense_id,
                              Expense.user_id==user.get("id"))
    )
    task_to_delete = response.scalar_one_or_none()
    if task_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense Not Found")
    await db.delete(task_to_delete)
    await db.commit()