from database import Base
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='User', nullable=False)