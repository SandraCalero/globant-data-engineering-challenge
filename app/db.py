from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends
import os

# Use the database URL from the environment variable
engine = create_engine(os.getenv("DATABASE_URL"))


def get_session():
    """
    Dependency that provides a SQLModel session for database operations.
    Yields a session to be used in FastAPI endpoints.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
