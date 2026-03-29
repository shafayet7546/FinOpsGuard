from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# sqlite with database finopsguard.db, for local development and testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./finopsguard.db"
# open connection to database, configured accordingly for FastAPI
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# produce new session with particular conditions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()