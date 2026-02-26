# API DB — session et base SQLAlchemy (RecyClique PostgreSQL).

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from api.config import get_settings

settings = get_settings()
Base = declarative_base()

engine = create_engine(
    settings.database_url or "sqlite:///./recyclic.sqlite",
    connect_args={"check_same_thread": False} if not settings.database_url else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency: session BDD pour les routes FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
