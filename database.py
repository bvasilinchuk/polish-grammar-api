from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Enable SQL logging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        logging.info("Database session created")
        yield db
    except Exception as e:
        logging.error(f"Database session error: {e}")
        raise
    finally:
        logging.info("Closing database session")
        db.close()
