from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from celery import Celery
from app.config import settings
from app.database import async_engine, Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Content Management & Summarization API",
    description="API for managing and summarizing various types of content with AI-powered categorization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Celery for async task processing
celery_app = Celery(
    "content_processor",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup"""
    logger.info("Starting up application...")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    logger.info(f"CORS Origins: {settings.cors_origins}")

    # Note: Database tables will be created via Alembic migrations
    # Don't use Base.metadata.create_all() in production


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down application...")
    await async_engine.dispose()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Content Management & Summarization API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "connected",
            "redis": "configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# Import and include routers
from app.api.routes import content, search, themes

app.include_router(content.router, prefix="/api/v1", tags=["Content"])
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(themes.router, prefix="/api/v1", tags=["Themes"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
