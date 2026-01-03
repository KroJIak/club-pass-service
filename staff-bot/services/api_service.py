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
    
    async def get_or_create_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get existing user or create a new one in the main users table."""
        try:
            response = await self.client.post(
                f"{self.base_url}{self.api_prefix}/v1/users/get-or-create",
                json={
                    "telegram_user_id": telegram_user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error getting/creating user: {e}")
            return None


# Global API service instance
api_service = APIService(
    base_url="http://api:8000",
    api_prefix="/api"
)

