from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DATABASE_URL = "sqlite:///./iso27001.db"
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    Path("./uploads").mkdir(exist_ok=True)
    Path("./backups").mkdir(exist_ok=True)
    Path("./backups/auto").mkdir(exist_ok=True)
    Path("./backups/deploy").mkdir(exist_ok=True)
    Path("./backups/rfc").mkdir(exist_ok=True)
    Path("./backups/manual").mkdir(exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
