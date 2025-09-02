from sqlmodel import SQLModel, create_engine
import os

DB_URL = os.getenv("DB_URL", "sqlite:///./db.sqlite3")
engine = create_engine(DB_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)