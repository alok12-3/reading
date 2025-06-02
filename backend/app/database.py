# backend/app/database.py
from sqlmodel import create_engine, Session, SQLModel as SQLModelBase
from .config import settings
# Ensure models are imported if create_db_and_tables is to be used directly with SQLModel.metadata
from . import models

engine = create_engine(str(settings.DATABASE_URL), echo=True)

def create_db_and_tables():
    SQLModelBase.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
