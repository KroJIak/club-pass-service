"""API client service for bot."""
import httpx
from typing import Optional, Dict, Any, List
from bot.core.config import settings


class APIService:
    """Service for interacting with API."""
    
    def __init__(self):
        self.base_url = f"{settings.API_URL}{settings.API_PREFIX}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def get_events(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get list of events."""
        try:
            # TODO: Replace with actual API call when ready
            # response = await self.client.get(f"{self.base_url}/v1/events", params={"active": active_only})
            # return response.json()
            return []  # Placeholder
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    async def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        try:
            # TODO: Replace with actual API call when ready
            # response = await self.client.get(f"{self.base_url}/v1/events/{event_id}")
            # return response.json()
            return None  # Placeholder
        except Exception as e:
            print(f"Error fetching event: {e}")
            return None
    
    async def get_ticket_types(self, event_id: int) -> List[Dict[str, Any]]:
        """Get ticket types for event."""
        try:
            # TODO: Replace with actual API call when ready
            # response = await self.client.get(f"{self.base_url}/v1/events/{event_id}/ticket-types")
            # return response.json()
            return []  # Placeholder
        except Exception as e:
            print(f"Error fetching ticket types: {e}")
            return []
    
    async def create_order(self, user_id: int, event_id: int, ticket_type_id: int, quantity: int, promocode: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create order."""
        try:
            # TODO: Replace with actual API call when ready
            # response = await self.client.post(f"{self.base_url}/v1/orders", json={
            #     "user_id": user_id,
            #     "event_id": event_id,
            #     "ticket_type_id": ticket_type_id,
            #     "quantity": quantity,
            #     "promocode": promocode
            # })
            # return response.json()
            return None  # Placeholder
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    async def get_user_tickets(self, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get user tickets."""
        try:
            # TODO: Replace with actual API call when ready
            # response = await self.client.get(f"{self.base_url}/v1/users/{user_id}/tickets", params={"active_only": active_only})
            # return response.json()
            return []  # Placeholder
        except Exception as e:
            print(f"Error fetching user tickets: {e}")
            return []


# Global instance
api_service = APIService()
