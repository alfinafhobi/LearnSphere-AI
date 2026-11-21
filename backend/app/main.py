
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base, SessionLocal
from .seed_data import seed_database
from .routers import (
    auth_router,
    subjects_router,
    assessment_router,
    planner_router,
    tutor_router,
    quiz_router,
    analytics_router,
    agents_router,
    profile_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)

    # Run seed data
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    yield


# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic AI-Based Personalized Learning and Academic Success System API",
    lifespan=lifespan
)


# Enable CORS for local development and Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://learn-sphere-ai-two.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include all API v1 routes
prefix = settings.API_V1_STR

app.include_router(auth_router, prefix=prefix)
app.include_router(subjects_router, prefix=prefix)
app.include_router(assessment_router, prefix=prefix)
app.include_router(planner_router, prefix=prefix)
app.include_router(tutor_router, prefix=prefix)
app.include_router(quiz_router, prefix=prefix)
app.include_router(analytics_router, prefix=prefix)
app.include_router(agents_router, prefix=prefix)
app.include_router(profile_router, prefix=prefix)


# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "demo_mode": settings.DEMO_MODE,
        "gemini_api_configured": bool(
            os.environ.get("GEMINI_API_KEY")
            or settings.GEMINI_API_KEY
        )
    }


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to LearnSphere AI - Agentic Academic Success Platform",
        "documentation": "/docs",
        "health": "/health"
    }

