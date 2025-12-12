import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    Resource,
    Alert,
    AlertType,
    AlertStatus,
    AuditLog,
)
from crud import get_resource
from alerting import deliver_alert, log_alert_event

# Configure logger
logger = logging.getLogger("security_events")
logger.setLevel(logging.INFO)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Security Event Detection Logic ---

# Example: Supported security event types
SECURITY_EVENT_TYPES = [
    "unauthorized_access",
    "configuration_change",
    "policy_violation",
    "privilege_escalation",
    "resource_exposure",
]

def detect_security_event(
    db: Session,
    resource_id: UUID,
    event_type: str,
    actor: Optional[str] = None,
    details: Optional[dict] = None,
) -> Alert:
    """
    Detects and handles a security-relevant event for a resource.
    Generates an alert, delivers it, and logs the event.
    """
    if event_type not in SECURITY_EVENT_TYPES:
        logger.warning(f"Unsupported security event type: {event_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported security event type: {event_type}"
        )
    resource = get_resource(db, resource_id)
    alert = Alert(
        resource_id=resource.id,
        type=AlertType.SECURITY,
        status=AlertStatus.ACTIVE,
        title=f"Security Event: {event_type.replace('_', ' ').title()}",
        description=f"Detected security event '{event_type}' on resource '{resource.name}'",
        triggered_at=datetime.utcnow(),
        severity="critical" if event_type in ["unauthorized_access", "privilege_escalation", "resource_exposure"] else "warning",
        details=details or {},
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    logger.info(f"Security alert generated: {alert.id} for event {event_type} on resource {resource.id}")

    # Deliver alert via channels and log event
    deliver_alert(db, alert)
    log_alert_event(
        db=db,
        alert=alert,
        event_type="security_event_detected",
        actor=actor or "system",
        details=details or {},
    )
    return alert

# --- FastAPI Router ---

from pydantic import BaseModel, Field

class SecurityEventIn(BaseModel):
    resource_id: UUID
    event_type: str
    actor: Optional[str] = None
    details: Optional[dict] = None

class SecurityAlertOut(BaseModel):
    id: UUID
    resource_id: Optional[UUID]
    type: str
    status: str
    title: str
    description: Optional[str]
    triggered_at: str
    resolved_at: Optional[str]
    severity: str
    details: Optional[dict]

    class Config:
        orm_mode = True

security_events_router = APIRouter()

@security_events_router.post("/security-events/detect", response_model=SecurityAlertOut, status_code=status.HTTP_201_CREATED)
def detect_security_event_endpoint(
    event: SecurityEventIn,
    db: Session = Depends(get_db)
):
    """
    Endpoint to detect and handle a security-relevant event for a resource.
    """
    alert = detect_security_event(
        db=db,
        resource_id=event.resource_id,
        event_type=event.event_type,
        actor=event.actor,
        details=event.details,
    )
    return alert

@security_events_router.get("/security-events/types", response_model=List[str])
def list_security_event_types():
    """
    List supported security event types.
    """
    return SECURITY_EVENT_TYPES

# Exported symbols
__all__ = [
    "security_events_router",
    "detect_security_event",
    "SECURITY_EVENT_TYPES",
]