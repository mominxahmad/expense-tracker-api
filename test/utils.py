from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from models import Base, Expense, User
import pytest
from routers.auth import bcrypt_context


# mock db setup for testing using sqlite
TEST_DATABASE_URL = "sqlite:///./testdb.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread":False},
                       poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base.metadata.create_all(bind=engine)


# to override dependencies
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_authenticate_current_user():
    return {
        "id": 1,
        "username": "test_user",
        "role": "admin"
    }


@pytest.fixture
def test_expense():
    db = TestingSessionLocal()
    expense = Expense(
        title = "gym membership",
        amount = 5000,
        category = "subscriptions",
        description = "Uni sept membership fee for the gym",
        user_id = 1
    )
    db.add(expense)
    db.commit()
    yield expense
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM expense;"))
        connection.commit()
    db.close()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = User(
        email = "test@email.com",
        username = "test_user",
        first_name = "f_test",
        last_name = "l_test",
        hashed_password = bcrypt_context.hash("testing123"),
        role = "admin"
    )
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM user;"))
        connection.commit()
    db.close()