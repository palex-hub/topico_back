from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carga el archivo .env
load_dotenv()

# Obtiene la URL completa
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Si por alguna razón la URL empieza con 'postgres://' (común en Heroku), 
# SQLAlchemy requiere 'postgresql://'. Este pequeño fix ayuda:
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()