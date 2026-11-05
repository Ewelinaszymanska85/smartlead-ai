import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.user_models import UserDB
from main import app
from app.jwt import create_access_token


TEST_DATABASE_URL = "sqlite:///./test_smartlead.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        # Przygotowanie kont testowych.
        db.add_all([
            UserDB(
                id=1,
                username="ewelina",
                password_hash="test-hash",
                role="admin"
            ),
            UserDB(
                id=2,
                username="testuser",
                password_hash="test-hash",
                role="user"
            ),
            UserDB(
                id=3,
                username="sales",
                password_hash="test-hash",
                role="sales"
            )
        ])

        db.commit()

        yield db

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    token = create_access_token({
        "sub": "ewelina",
        "role": "admin",
        "user_id": 1
    })

    return {
        "Authorization": f"Bearer {token}"
    }