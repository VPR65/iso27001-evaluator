import os
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./iso27001.db")

if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
else:
    engine = create_engine(
        DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
    )


def create_db_and_tables():
    if DATABASE_URL.startswith("postgresql"):
        Path("./uploads").mkdir(exist_ok=True)
        Path("./backups").mkdir(exist_ok=True)
        Path("./backups/auto").mkdir(exist_ok=True)
        Path("./backups/deploy").mkdir(exist_ok=True)
        Path("./backups/rfc").mkdir(exist_ok=True)
        Path("./backups/manual").mkdir(exist_ok=True)
    else:
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
