# Car Accident Alert System - Backend

This is the backend component of the Car Accident Alert System, built with FastAPI and Python.

## Features

- User authentication with JWT
- Accident data ingestion and storage
- Real-time accident detection using ML models
- Emergency contact management
- Alert notifications via SMS and email
- RESTful API with OpenAPI documentation

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **ML**: TensorFlow/Keras for accident detection
- **Authentication**: JWT tokens
- **Notifications**: Twilio (SMS) and SendGrid (Email)
- **Deployment**: Docker

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (see `.env.example`)

3. Run database migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/              # API routers
├── core/             # Core configuration and security
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── utils/            # Utility functions
├── ml/               # Machine learning components
├── alembic/          # Database migrations
├── tests/            # Unit and integration tests
├── requirements.txt  # Python dependencies
└── main.py           # Application entry point
```

## Environment Variables

Create a `.env` file with the following variables:

```
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=car_accident_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Twilio (for SMS)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=your-twilio-number

# SendGrid (for Email)
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=your-email@example.com
```