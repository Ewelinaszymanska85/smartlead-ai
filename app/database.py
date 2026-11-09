import os
import ssl

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker


# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv()


# Pobranie adresu bazy danych.
# Domyślnie lokalnie korzystamy z SQLite.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smartlead.db"
)


# Konfiguracja połączenia z bazą danych.
connect_args = {}


# Konfiguracja PostgreSQL z wykorzystaniem sterownika pg8000.
if DATABASE_URL.startswith(("postgres://", "postgresql://")):
    url = make_url(DATABASE_URL)

    # Usunięcie parametrów przeznaczonych dla sterownika libpq.
    query = {
        key: value
        for key, value in url.query.items()
        if key not in ("sslmode", "channel_binding")
    }

    # Wybór sterownika pg8000.
    DATABASE_URL = url.set(
        drivername="postgresql+pg8000",
        query=query
    ).render_as_string(hide_password=False)

    # Bezpieczne połączenie SSL z PostgreSQL.
    connect_args = {
        "ssl_context": ssl.create_default_context()
    }


# SQLite wymaga specjalnego parametru połączenia.
elif DATABASE_URL.startswith("sqlite"):
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