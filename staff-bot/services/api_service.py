"""API service for staff bot."""
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class APIService:
    """Service for making API requests."""
    
    def __init__(self, base_url: str, api_prefix: str = "/api"):
        self.base_url = base_url.rstrip('/')
        self.api_prefix = api_prefix.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def check_staff_access(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Check if user has staff access."""
        try:
            response = await self.client.get(
                f"{self.base_url}{self.api_prefix}/v1/staff/check-access",
                params={"telegram_user_id": telegram_user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error checking staff access: {e}")
            return None


# Global API service instance
api_service = APIService(
    base_url="http://api:8000",
    api_prefix="/api"
)

