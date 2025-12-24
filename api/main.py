"""API Service Entry Point."""
import logging
import subprocess
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.api.routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
)

# CORS middleware
# Parse CORS origins - if "*", use wildcard, otherwise split by comma
if settings.CORS_ORIGINS == "*":
    cors_origins = ["*"]
    allow_credentials = False  # Cannot use credentials with wildcard
else:
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup."""
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app",
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            logger.info("Database migrations completed successfully")
        else:
            logger.error(f"Migration failed: {result.stderr}")
            # Don't exit - let the app start anyway, migrations can be run manually
    except Exception as e:
        logger.error(f"Error running migrations: {e}", exc_info=True)
        # Don't exit - let the app start anyway, migrations can be run manually


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Club Pass Service API",
        "version": settings.API_VERSION,
        "status": "running",
    }
