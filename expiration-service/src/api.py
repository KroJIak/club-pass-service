"""FastAPI application for expiration service."""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from src.db import SessionLocal
from src.models.event import Event
from src.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)

app = FastAPI(title="Expiration Service API")


class UpdateIntervalRequest(BaseModel):
    """Request model for updating check interval."""
    check_interval_minutes: int


class UpdateIntervalResponse(BaseModel):
    """Response model for updating check interval."""
    success: bool
    message: str
    current_interval: Optional[int] = None


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
    db: Session = SessionLocal()
    try:
        # Get event
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            logger.warning(f"Event {event_id} not found, skipping deactivation")
            return
        
        # Deactivate event
        if event.is_active:
            event.is_active = False
            logger.info(f"Deactivated event {event_id} ({event.name})")
        
        # Mark all active tickets for this event as expired
        tickets = db.query(Ticket).filter(
            Ticket.event_id == event_id,
            Ticket.status == TicketStatus.ACTIVE
        ).all()
        
        expired_count = 0
        for ticket in tickets:
            ticket.status = TicketStatus.EXPIRED
            expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Marked {expired_count} ticket(s) as expired for event {event_id}")
        
        db.commit()
        logger.info(f"Successfully deactivated event {event_id} and expired {expired_count} ticket(s)")
    except Exception as e:
        logger.error(f"Error deactivating event {event_id}: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/update-interval", response_model=UpdateIntervalResponse)
async def update_interval(request: UpdateIntervalRequest):
    """Update the check interval for expiration checks."""
    global _scheduler
    
    if _scheduler is None:
        return UpdateIntervalResponse(
            success=False,
            message="Scheduler not initialized"
        )
    
    if request.check_interval_minutes < 1:
        return UpdateIntervalResponse(
            success=False,
            message="check_interval_minutes must be at least 1"
        )
    
    try:
        from apscheduler.triggers.interval import IntervalTrigger
        
        job = _scheduler.get_job('check_expirations')
        if job:
            current_interval = job.trigger.interval.total_seconds() / 60
            logger.info(f"Updating check interval from {current_interval} to {request.check_interval_minutes} minutes")
            _scheduler.reschedule_job(
                'check_expirations',
                trigger=IntervalTrigger(minutes=request.check_interval_minutes)
            )
            return UpdateIntervalResponse(
                success=True,
                message=f"Interval updated to {request.check_interval_minutes} minutes",
                current_interval=request.check_interval_minutes
            )
        else:
            return UpdateIntervalResponse(
                success=False,
                message="Check job not found"
            )
    except Exception as e:
        logger.error(f"Error updating interval: {e}", exc_info=True)
        return UpdateIntervalResponse(
            success=False,
            message=f"Error updating interval: {str(e)}"
        )


@app.post("/schedule-event-deactivation", response_model=ScheduleEventDeactivationResponse)
async def schedule_event_deactivation(request: ScheduleEventDeactivationRequest):
    """Schedule deactivation of a specific event at a specific time."""
    global _scheduler
    
    if _scheduler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scheduler not initialized"
        )
    
    try:
        # Parse datetime
        deactivation_dt = datetime.fromisoformat(request.deactivation_datetime.replace('Z', '+00:00'))
        
        # Check if datetime is in the future
        if deactivation_dt <= datetime.now(deactivation_dt.tzinfo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deactivation datetime must be in the future"
            )
        
        # Check if event exists
        db: Session = SessionLocal()
        try:
            event = db.query(Event).filter(Event.id == request.event_id).first()
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event {request.event_id} not found"
                )
        finally:
            db.close()
        
        # Remove existing job for this event if it exists
        job_id = f"deactivate_event_{request.event_id}"
        if _scheduler.get_job(job_id):
            _scheduler.remove_job(job_id)
            logger.info(f"Removed existing deactivation job for event {request.event_id}")
        
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
        
        logger.info(f"Scheduled deactivation of event {request.event_id} for {deactivation_dt}")
        
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
