import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("intellichat")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown."""
    logger.info("Starting up IntelliChat backend...")
    # Initialize database tables asynchronously
    await init_db()
    logger.info("IntelliChat backend startup complete.")
    yield
    logger.info("Shutting down IntelliChat backend...")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Modern, intelligent AI chatbot backend API powered by FastAPI, SQLAlchemy async, and multi-provider LLMs.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else [settings.ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing service metadata."""
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "auth": "/api/v1/auth",
            "conversations": "/api/v1/conversations",
            "chat_stream": "/api/v1/chat/stream",
            "models": "/api/v1/models",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify service and database operational readiness."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": "connected",
        "default_model": settings.DEFAULT_MODEL,
        "default_provider": settings.DEFAULT_LLM_PROVIDER,
    }


# Include V1 API Router
app.include_router(api_v1_router)
