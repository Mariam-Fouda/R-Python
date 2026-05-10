import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client):
    client.post("/api/auth/register", json={
        "username": "testadmin",
        "email": "admin@test.com",
        "password": "adminpass123",
        "role": "admin",
    })
    res = client.post("/api/auth/login", json={"username": "testadmin", "password": "adminpass123"})
    return res.json()["access_token"]


@pytest.fixture(scope="function")
def student_token(client):
    client.post("/api/auth/register", json={
        "username": "teststudent",
        "email": "student@test.com",
        "password": "studentpass123",
        "role": "student",
    })
    res = client.post("/api/auth/login", json={"username": "teststudent", "password": "studentpass123"})
    return res.json()["access_token"]
