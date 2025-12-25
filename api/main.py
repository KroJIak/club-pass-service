"""API Service Entry Point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.api.routes import api_router

# Configure logging - always use DEBUG level for detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=True,  # Always enabled for detailed error messages
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Club Pass Service API",
        "version": settings.API_VERSION,
        "status": "running",
    }
