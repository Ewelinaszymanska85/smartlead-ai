import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv()


# Lokalnie używamy SQLite, a po wdrożeniu możemy podać adres PostgreSQL.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smartlead.db"
)


# Dostosowanie adresu PostgreSQL do formatu SQLAlchemy.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# SQLite wymaga specjalnego parametru połączenia.
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


# Utworzenie połączenia z bazą danych.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


# Konfiguracja sesji bazy danych.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Baza modeli SQLAlchemy.
Base = declarative_base()


# Udostępnianie sesji bazodanowej endpointom.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()