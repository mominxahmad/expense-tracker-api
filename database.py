import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
async_SessionLocal = async_sessionmaker(bind=async_engine,expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with async_SessionLocal() as db:
        yield db