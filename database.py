from contextvars import ContextVar
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

# Example: adjust to your real DATABASE_URL
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/casbin"

engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Holds the current tenant id for the request (if any)
current_tenant_id: ContextVar[Optional[int]] = ContextVar("current_tenant_id", default=None)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables (for simple setups; use Alembic in production)."""
    Base.metadata.create_all(bind=engine)