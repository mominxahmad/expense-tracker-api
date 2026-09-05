from fastapi import FastAPI
from starlette import status
import models
from database import engine
from routers import auth,expenses


app=FastAPI(
    title="Expense Tracker API",
    description="REST API for managing personal expenses with JWT authentication",
    version="1.0.0"
)


models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/", status_code=status.HTTP_200_OK, tags=["API"])
async def api_root():
    return {
        "name": "Expense Tracker API",
        "version": "1.0.0",
        "description": "REST API for managing personal expenses with JWT authentication"
    }

@app.get("/health", status_code=status.HTTP_200_OK, tags=["API"])
async def api_health_check():
    return {
        "status" : "healthy"
    }