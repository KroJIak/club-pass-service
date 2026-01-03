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
# Combine admin panel and mini app origins
cors_origins_list = []

if settings.CORS_ORIGINS == "*":
    cors_origins = ["*"]
    allow_credentials = False  # Cannot use credentials with wildcard
else:
    cors_origins_list.extend([origin.strip() for origin in settings.CORS_ORIGINS.split(",")])

# Add mini app origins if specified
if settings.CORS_ORIGINS_MINI_APP:
    mini_app_origins = [origin.strip() for origin in settings.CORS_ORIGINS_MINI_APP.split(",")]
    cors_origins_list.extend(mini_app_origins)

if cors_origins_list:
    cors_origins = list(set(cors_origins_list))  # Remove duplicates
    allow_credentials = True
else:
    cors_origins = ["*"]
    allow_credentials = False

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
