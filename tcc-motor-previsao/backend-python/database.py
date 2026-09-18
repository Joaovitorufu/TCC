from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Criação do banco de dados SQLite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./hospital_forecast.db"

# Para usar o SQLite com a engine do SQLAlchemy precisamos usar check_same_thread: False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
