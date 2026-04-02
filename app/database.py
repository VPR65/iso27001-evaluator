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


def _run_postgresql_migrations():
    """Run manual migrations for PostgreSQL since create_all doesn't alter tables."""
    from sqlalchemy import text

    with engine.begin() as conn:
        # Add two_factor columns to users table if they don't exist
        columns_to_add = [
            ("two_factor_enabled", "BOOLEAN DEFAULT FALSE"),
            ("two_factor_secret", "VARCHAR"),
            ("two_factor_verified", "BOOLEAN DEFAULT FALSE"),
        ]
        for col_name, col_type in columns_to_add:
            conn.execute(
                text(
                    f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                )
            )


def create_db_and_tables():
    if DATABASE_URL.startswith("postgresql"):
        Path("./uploads").mkdir(exist_ok=True)
        Path("./backups").mkdir(exist_ok=True)
        Path("./backups/auto").mkdir(exist_ok=True)
        Path("./backups/deploy").mkdir(exist_ok=True)
        Path("./backups/rfc").mkdir(exist_ok=True)
        Path("./backups/manual").mkdir(exist_ok=True)
        SQLModel.metadata.create_all(engine)
        _run_postgresql_migrations()
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
