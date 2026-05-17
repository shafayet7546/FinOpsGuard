import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# SQLite is the primary database for local development and default runtime.
# can be overriden with DATABASE_URL (easy transition to PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finopsguard.db")

# check_same_thread only needed for SQLite's single-thread constraint
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
