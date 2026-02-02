<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# This will pick up your Supabase URI from Cloud Run Environment Variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# If using Supabase/Postgres, we don't need check_same_thread
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
=======
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

database_url = os.getenv("DATABASE_URL")

# Supabase fix for SQLAlchemy
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Create engine only if database_url is available
engine = None
SessionLocal = None

if database_url:
    # connect_args are vital for Supabase SSL
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """Initialize database tables"""
    if engine is None:
        raise RuntimeError("Database engine not initialized - DATABASE_URL not set")
    from models import Chat  # Import here to avoid circular dependency
    Base.metadata.create_all(bind=engine)
>>>>>>> b72a9f6 (backend)
