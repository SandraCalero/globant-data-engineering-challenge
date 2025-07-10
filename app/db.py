from sqlmodel import Session, create_engine
from typing import Annotated
from fastapi import Depends
import os

# Use the database URL from the environment variable
engine = create_engine(os.getenv("DATABASE_URL"))


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
