import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base

# Database connection URL - defaulting to a local PostgreSQL instance
# In a real scenario, this would be loaded from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/cv_rct_db")

def get_engine(url=DATABASE_URL):
    return create_engine(url)

def init_db(engine):
    Base.metadata.create_all(engine)

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    # Simple script to initialize the DB if run directly
    print(f"Initializing database at {DATABASE_URL}...")
    try:
        engine = get_engine()
        init_db(engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Note: Make sure PostgreSQL is running and the database 'cv_rct_db' exists.")
