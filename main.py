from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette import status
import models
from database import async_engine
from routers import auth,expenses,admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn: #app starts
        await conn.run_sync(models.Base.metadata.create_all) #creates tables
    yield #for when app is live
    await async_engine.dispose() #when app ends


app=FastAPI(
    title="Expense Tracker API",
    description="Async REST API for managing personal expenses with JWT authentication",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(admin.router)


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