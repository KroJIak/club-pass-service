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
            response = await self.client.get(
                f"{self.base_url}/v1/events",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("events", [])
        except httpx.HTTPError as e:
            print(f"Error fetching events: {e}")
            return []
    
    async def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/v1/events/{event_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching event: {e}")
            return None
    
    async def get_ticket_types(self, event_id: int) -> List[Dict[str, Any]]:
        """Get ticket types for event."""
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/events/{event_id}/ticket-types",
                params={"active_only": True}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("ticket_types", [])
        except httpx.HTTPError as e:
            print(f"Error fetching ticket types: {e}")
            return []
    
    async def create_order(
        self,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        quantity: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create an order and get payment invoice data."""
        import logging
        logger = logging.getLogger(__name__)
        
        request_data = {
            "user_id": user_id,
            "event_id": event_id,
            "ticket_type_id": ticket_type_id,
            "quantity": quantity,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }
        logger.info(f"Creating order: {request_data}, base_url={self.base_url}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/orders",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating order: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                    logger.error(f"Error detail: {error_detail}")
                    print(f"Error detail: {error_detail}")
                except Exception as parse_error:
                    logger.error(f"Failed to parse error response: {parse_error}")
                    try:
                        error_text = e.response.text
                        logger.error(f"Error response text: {error_text}")
                        print(f"Error response text: {error_text}")
                    except:
                        pass
            return None
    
    async def get_user_tickets(self, telegram_user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get user tickets by Telegram user ID."""
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/users/telegram/{telegram_user_id}/tickets",
                params={"active_only": active_only}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("tickets", [])
        except httpx.HTTPError as e:
            print(f"Error fetching user tickets: {e}")
            return []
    
    async def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Get ticket by ID."""
        try:
            response = await self.client.get(f"{self.base_url}/v1/tickets/{ticket_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching ticket: {e}")
            return None
    
    async def complete_order_mock(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Complete order in mock mode (for testing without payment)."""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/orders/{order_id}/complete-mock"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error completing mock order: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                    print(f"Error detail: {error_detail}")
                except:
                    pass
            return None
    
    async def create_or_update_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create or update a user."""
        try:
            request_data = {
                "telegram_user_id": telegram_user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name
            }
            response = await self.client.post(
                f"{self.base_url}/v1/users/get-or-create",
                json=request_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Don't log as error - user creation is not critical for /start
            print(f"Error creating/updating user: {e}")
            return None
    
    async def refund_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Refund a ticket (mark as refunded)."""
        try:
            response = await self.client.post(
                f"{self.base_url}/v1/tickets/{ticket_id}/refund"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error refunding ticket: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                    print(f"Error detail: {error_detail}")
                except:
                    pass
            return None
    
    async def get_club_settings(self) -> Optional[Dict[str, Any]]:
        """Get club settings from API."""
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/users/club-settings"
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Error fetching club settings: {e}")
            return None
    
    async def get_menu_photos(self) -> List[Dict[str, Any]]:
        """Get menu photos from API."""
        try:
            response = await self.client.get(
                f"{self.base_url}/v1/users/menu-photos"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("photos", [])
        except httpx.HTTPError as e:
            print(f"Error fetching menu photos: {e}")
            return []
    
    async def create_support_message(self, user_id: int, message: str, photo_paths: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Create a support message."""
        try:
            payload = {"user_id": user_id, "message": message}
            if photo_paths:
                payload["photo_paths"] = photo_paths
            
            response = await self.client.post(
                f"{self.base_url}/v1/users/support-messages",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating support message: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                    logger.error(f"Error detail: {error_detail}")
                except:
                    pass
            return None
    
    async def search_music(self, song_title: str, artist: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search for music tracks using music-search service."""
        try:
            # Use music-search service (running on port 8004)
            music_search_url = "http://music-search:8004"
            request_data = {"song_title": song_title}
            if artist:
                request_data["artist"] = artist
            
            response = await self.client.post(
                f"{music_search_url}/search",
                json=request_data,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error searching music: {e}")
            return None
    
    async def create_music_request(
        self,
        telegram_user_id: int,
        track_title: str,
        track_artist: Optional[str] = None,
        yandex_music_url: Optional[str] = None,
        other_source_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a music request."""
        try:
            request_data = {
                "track_title": track_title,
                "track_artist": track_artist,
                "yandex_music_url": yandex_music_url,
                "other_source_url": other_source_url
            }
            response = await self.client.post(
                f"{self.base_url}/v1/users/music-requests",
                json=request_data,
                params={"telegram_user_id": telegram_user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating music request: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                    logger.error(f"Error detail: {error_detail}")
                    # Return error detail for handling
                    return {"error": error_detail}
                except:
                    pass
            return None


# Global instance
api_service = APIService()
