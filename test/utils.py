from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from models import Base, Expense, User
from routers.auth import bcrypt_context, authenticate_current_user
from database import get_db
from fastapi.testclient import TestClient
from main import app
import pytest
import pytest_asyncio


TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


client = TestClient(app)


async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db


def override_authenticate_current_user():
    return {
        "id": 1,
        "username": "test_user",
        "role": "admin"
    }


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[authenticate_current_user] = override_authenticate_current_user


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def test_expense():
    async with TestingSessionLocal() as db:
        expense = Expense(
            title="gym membership",
            amount=5000,
            category="subscriptions",
            description="Uni sept membership fee for the gym",
            user_id=1
        )
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        yield expense


@pytest_asyncio.fixture
async def test_user():
    async with TestingSessionLocal() as db:
        user = User(
            email="test@email.com",
            username="test_user",
            first_name="f_test",
            last_name="l_test",
            hashed_password=bcrypt_context.hash("testing123"),
            role="admin"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        yield user