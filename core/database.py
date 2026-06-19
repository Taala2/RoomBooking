from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


db_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/room_booking?client_encoding=utf8"

engine = create_engine(db_url, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close_all()