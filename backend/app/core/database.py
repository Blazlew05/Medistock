"""Configuracion de SQLAlchemy y sesion de base de datos."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injection para obtener sesion de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
