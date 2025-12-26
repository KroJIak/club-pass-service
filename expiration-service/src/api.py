"""FastAPI application for expiration service."""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.models.event import Event
from src.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)

app = FastAPI(title="Expiration Service API")


class ScheduleEventDeactivationRequest(BaseModel):
    """Request model for scheduling event deactivation."""
    event_id: int
    deactivation_datetime: str  # ISO format: "YYYY-MM-DDTHH:MM:SS"


class ScheduleEventDeactivationResponse(BaseModel):
    """Response model for scheduling event deactivation."""
    success: bool
    message: str
    event_id: int
    scheduled_time: str


# Global scheduler reference (will be set by main.py)
_scheduler = None


def set_scheduler(scheduler):
    """Set the scheduler instance for API endpoints."""
    global _scheduler
    _scheduler = scheduler


def deactivate_event_and_tickets(event_id: int):
    """Deactivate an event and mark all its tickets as expired."""
    logger.info("=" * 60)
    logger.info(f"⏰ EXECUTING: Deactivating event {event_id} and expiring tickets")
    logger.info(f"   Current time: {datetime.now()}")
    
    db: Session = SessionLocal()
    try:
        # Get event
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            logger.warning(f"❌ Event {event_id} not found, skipping deactivation")
            return
        
        logger.info(f"✅ Event found: ID={event.id}, Name='{event.name}'")
        logger.info(f"   Event current status: is_active={event.is_active}")
        
        # Deactivate event
        if event.is_active:
            event.is_active = False
            logger.info(f"🔄 Deactivated event {event_id} ({event.name})")
        else:
            logger.info(f"ℹ️  Event {event_id} is already inactive, skipping deactivation")
        
        # Mark all active tickets for this event as expired
        tickets = db.query(Ticket).filter(
            Ticket.event_id == event_id,
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        logger.info(f"📋 Found {len(tickets)} active ticket(s) for event {event_id}")
        
        expired_count = 0
        for ticket in tickets:
            ticket.status = TicketStatus.EXPIRED
            expired_count += 1
            logger.debug(f"   Expired ticket {ticket.id} (token: {ticket.token})")
        
        if expired_count > 0:
            logger.info(f"✅ Marked {expired_count} ticket(s) as expired for event {event_id}")
        else:
            logger.info(f"ℹ️  No active tickets to expire for event {event_id}")
        
        db.commit()
        logger.info(f"✅ Successfully completed deactivation:")
        logger.info(f"   Event {event_id} deactivated: {not event.is_active}")
        logger.info(f"   Tickets expired: {expired_count}")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Error deactivating event {event_id}: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/schedule-event-deactivation", response_model=ScheduleEventDeactivationResponse)
async def schedule_event_deactivation(request: ScheduleEventDeactivationRequest):
    """Schedule deactivation of a specific event at a specific time."""
    global _scheduler
    
    logger.info("=" * 60)
    logger.info(f"📅 RECEIVED REQUEST: Schedule deactivation for event {request.event_id}")
    logger.info(f"   Deactivation datetime: {request.deactivation_datetime}")
    
    if _scheduler is None:
        logger.error("❌ Scheduler not initialized!")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler not initialized"
        )
    
    try:
        # Parse datetime
        deactivation_dt = datetime.fromisoformat(request.deactivation_datetime.replace('Z', '+00:00'))
        current_time = datetime.now(deactivation_dt.tzinfo) if deactivation_dt.tzinfo else datetime.now()
        
        logger.info(f"   Parsed datetime: {deactivation_dt}")
        logger.info(f"   Current time: {current_time}")
        logger.info(f"   Time until deactivation: {deactivation_dt - current_time}")
        
        # Check if datetime is in the future
        if deactivation_dt <= current_time:
            logger.warning(f"⚠️  Deactivation datetime is in the past! Rejecting request.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deactivation datetime must be in the future"
            )
        
        # Check if event exists
        db: Session = SessionLocal()
        try:
            event = db.query(Event).filter(Event.id == request.event_id).first()
            if not event:
                logger.error(f"❌ Event {request.event_id} not found in database!")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event {request.event_id} not found"
                )
            
            logger.info(f"✅ Event found: ID={event.id}, Name='{event.name}'")
            logger.info(f"   Event is_active: {event.is_active}")
            logger.info(f"   Event start: {event.start_date} {event.start_time}")
            logger.info(f"   Event end: {event.end_date} {event.end_time}")
        finally:
            db.close()
        
        # Remove existing job for this event if it exists
        job_id = f"deactivate_event_{request.event_id}"
        existing_job = _scheduler.get_job(job_id)
        if existing_job:
            logger.info(f"🔄 Removing existing deactivation job for event {request.event_id}")
            logger.info(f"   Previous scheduled time: {existing_job.next_run_time}")
            _scheduler.remove_job(job_id)
            logger.info(f"✅ Existing job removed")
        
        # Schedule new job
        from apscheduler.triggers.date import DateTrigger
        
        _scheduler.add_job(
            deactivate_event_and_tickets,
            trigger=DateTrigger(run_date=deactivation_dt),
            id=job_id,
            name=f"Deactivate event {request.event_id}",
            replace_existing=True,
            args=[request.event_id]
        )
        
        logger.info(f"✅ Successfully scheduled deactivation job")
        logger.info(f"   Job ID: {job_id}")
        logger.info(f"   Scheduled time: {deactivation_dt}")
        logger.info(f"   Event will be deactivated and all tickets expired at this time")
        logger.info("=" * 60)
        
        return ScheduleEventDeactivationResponse(
            success=True,
            message=f"Event {request.event_id} scheduled for deactivation at {deactivation_dt}",
            event_id=request.event_id,
            scheduled_time=deactivation_dt.isoformat()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error scheduling event deactivation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling event deactivation: {str(e)}"
        )


@app.delete("/cancel-event-deactivation/{event_id}")
async def cancel_event_deactivation(event_id: int):
    """Cancel scheduled deactivation for an event."""
    global _scheduler
    
    if _scheduler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler not initialized"
        )
    
    job_id = f"deactivate_event_{event_id}"
    job = _scheduler.get_job(job_id)
    
    if job:
        _scheduler.remove_job(job_id)
        logger.info(f"Cancelled deactivation job for event {event_id}")
        return {"success": True, "message": f"Deactivation cancelled for event {event_id}"}
    else:
        return {"success": False, "message": f"No scheduled deactivation found for event {event_id}"}
