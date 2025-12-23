"""Main API router."""
from fastapi import APIRouter

from api.api import health
from api.api.v1 import events, tickets, payments, admin, users

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/v1")
api_router.include_router(users.router, prefix="/v1/users")
api_router.include_router(events.router, prefix="/v1")
api_router.include_router(tickets.router, prefix="/v1")
api_router.include_router(payments.router, prefix="/v1")
api_router.include_router(admin.router, prefix="/v1")
