"""Ticket business logic service."""
from typing import List, Optional
from sqlalchemy.orm import Session
from api.repositories.ticket_repository import TicketRepository
from api.repositories.ticket_type_repository import TicketTypeRepository
from api.repositories.user_repository import UserRepository
from api.models.ticket import Ticket, TicketStatus
from api.api.v1.schemas import TicketDetailResponse


class TicketService:
    """Service for ticket operations."""
    
    @staticmethod
    def create_tickets_for_order(
        db: Session,
        user_id: int,
        event_id: int,
        ticket_type_id: int,
        quantity: int,
    ) -> List[Ticket]:
        """
        Create tickets for an order after successful payment.
        
        Args:
            db: Database session
            user_id: User ID
            event_id: Event ID
            ticket_type_id: Ticket type ID
            quantity: Number of tickets to create
        
        Returns:
            List of created tickets
        
        Raises:
            ValueError: If ticket type doesn't have enough availability
        """
        # Check availability
        if not TicketTypeRepository.check_availability(db, ticket_type_id, quantity):
            raise ValueError(f"Not enough tickets available for ticket type {ticket_type_id}")
        
        # Create tickets
        tickets = TicketRepository.create_batch(
            db, user_id, event_id, ticket_type_id, quantity
        )
        
        # Decrease availability
        TicketTypeRepository.decrease_availability(db, ticket_type_id, quantity)
        
        return tickets
    
    @staticmethod
    def get_user_tickets(
        db: Session,
        user_id: int,
        active_only: bool = False,
    ) -> List[Ticket]:
        """
        Get tickets for a user.
        
        Args:
            db: Database session
            user_id: User ID
            active_only: If True, return only active tickets
        
        Returns:
            List of tickets with related data
        """
        return TicketRepository.get_by_user_id(db, user_id, active_only=active_only)
    
    @staticmethod
    def get_ticket_by_id(
        db: Session,
        ticket_id: int,
    ) -> Optional[TicketDetailResponse]:
        """
        Get ticket by ID with all related data.
        
        Args:
            db: Database session
            ticket_id: Ticket ID
        
        Returns:
            Ticket detail response or None
        """
        ticket = TicketRepository.get_by_id(db, ticket_id)
        if not ticket:
            return None
        
        return TicketDetailResponse.model_validate(ticket)
    
    @staticmethod
    def refund_ticket(
        db: Session,
        ticket_id: int,
    ) -> Ticket:
        """
        Refund a ticket (mark as refunded).
        
        Args:
            db: Database session
            ticket_id: Ticket ID
        
        Returns:
            Refunded ticket
        
        Raises:
            ValueError: If ticket is used or already refunded
        """
        return TicketRepository.refund_ticket(db, ticket_id)
    
    @staticmethod
    def mark_ticket_as_used(
        db: Session,
        ticket_id: int,
    ) -> Optional[Ticket]:
        """
        Mark ticket as used.
        
        Args:
            db: Database session
            ticket_id: Ticket ID
        
        Returns:
            Updated ticket or None
        """
        return TicketRepository.mark_as_used(db, ticket_id)
