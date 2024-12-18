from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@postgres:5432/mydatabase")

# Create the database engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def create_connection():
    """Context manager for database connections."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to use in routes
def get_db():
    """Provide a database session for dependency injection."""
    with create_connection() as db:
        yield db
