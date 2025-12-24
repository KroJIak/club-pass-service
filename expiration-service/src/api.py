"""FastAPI application for expiration service."""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import logging

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


# Global scheduler reference (will be set by main.py)
_scheduler = None


def set_scheduler(scheduler):
    """Set the scheduler instance for API endpoints."""
    global _scheduler
    _scheduler = scheduler


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

