from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import users, accidents, contacts, alerts, ml
from .core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Car Accident Alert System with AI/ML Integration",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(accidents.router, prefix="/api/v1/accidents", tags=["accidents"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(ml.router, prefix="/api/v1/ml", tags=["ml"])

@app.get("/")
async def root():
    return {"message": "Car Accident Alert System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Only create tables when not in test mode
if __name__ != "__main__":
    # Import here to avoid circular imports during testing
    from .core.database import engine, Base
    Base.metadata.create_all(bind=engine)