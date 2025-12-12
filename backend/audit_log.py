import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    AuditLog,
    Incident,
    Alert,
)
from crud import get_incident, get_alert

# Configure logger
logger = logging.getLogger("audit_log")
logger.setLevel(logging.INFO)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Audit Log Query Logic ---

def get_audit_log(db: Session, audit_log_id: UUID) -> AuditLog:
    audit_log = db.query(AuditLog).filter(AuditLog.id == audit_log_id).first()
    if not audit_log:
        logger.warning(f"Audit log not found: {audit_log_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log entry not found."
        )
    return audit_log

def get_audit_logs(
    db: Session,
    incident_id: Optional[UUID] = None,
    alert_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if incident_id:
        query = query.filter(AuditLog.incident_id == incident_id)
    if alert_id:
        query = query.filter(AuditLog.alert_id == alert_id)
    return query.order_by(AuditLog.event_time.desc()).offset(skip).limit(limit).all()

# --- FastAPI Router ---

from pydantic import BaseModel, Field

class AuditLogOut(BaseModel):
    id: UUID
    incident_id: Optional[UUID]
    alert_id: Optional[UUID]
    event_type: str
    event_time: str
    actor: Optional[str]
    details: Optional[dict]

    class Config:
        orm_mode = True

audit_log_router = APIRouter()

@audit_log_router.get("/", response_model=List[AuditLogOut])
def list_audit_logs(
    incident_id: Optional[UUID] = Query(None),
    alert_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List audit log entries, optionally filtered by incident or alert.
    """
    logs = get_audit_logs(db, incident_id=incident_id, alert_id=alert_id, skip=skip, limit=limit)
    return logs

@audit_log_router.get("/{audit_log_id}", response_model=AuditLogOut)
def get_audit_log_endpoint(audit_log_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific audit log entry by ID.
    """
    log = get_audit_log(db, audit_log_id)
    return log

# Exported symbols
__all__ = [
    "audit_log_router",
    "get_audit_log",
    "get_audit_logs",
]