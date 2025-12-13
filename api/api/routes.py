"""Main API router."""
from fastapi import APIRouter

from api.api import health

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/v1")
