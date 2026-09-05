from fastapi import FastAPI
import models
from database import engine
from routers import auth


app=FastAPI(
    title="Expense Tracker API",
    description="An expense tracker api to practice my FastAPI learnings"
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)