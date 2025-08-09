import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base, get_db
from backend.models import models

# Create a test app
test_app = FastAPI()

# Add root and health check routes
@test_app.get("/")
async def root():
    return {"message": "Car Accident Alert System API"}

@test_app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(test_db):
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    # Import and include routers here to avoid database connection during import
    from backend.api import users, accidents, contacts, alerts, ml
    test_app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    test_app.include_router(accidents.router, prefix="/api/v1/accidents", tags=["accidents"])
    test_app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
    test_app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
    test_app.include_router(ml.router, prefix="/api/v1/ml", tags=["ml"])
    
    test_app.dependency_overrides[get_db] = override_get_db
    with TestClient(test_app) as client:
        yield client
    test_app.dependency_overrides.clear()

# Main tests
def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Car Accident Alert System API"}

def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

# User tests
def test_create_user(test_client):
    response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "phone_number": "+1234567890"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert data["is_active"] == True

def test_create_user_duplicate(test_client):
    # Create first user
    test_client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "phone_number": "+1234567890"
        }
    )
    
    # Try to create duplicate
    response = test_client.post(
        "/api/v1/users/",
        json={
            "email": "duplicate@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "phone_number": "+1234567890"
        }
    )
    assert response.status_code == 400

def test_login_user(test_client):
    # Create user
    test_client.post(
        "/api/v1/users/",
        json={
            "email": "login@example.com",
            "password": "loginpassword",
            "full_name": "Login User",
            "phone_number": "+1234567890"
        }
    )
    
    # Login
    response = test_client.post(
        "/api/v1/users/login",
        json={
            "email": "login@example.com",
            "password": "loginpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"