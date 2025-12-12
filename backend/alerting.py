import logging
import smtplib
from typing import List, Optional
from uuid import UUID
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    Alert,
    AlertStatus,
    AlertType,
    Incident,
    AuditLog,
)
from crud import get_alert, get_alerts, get_incident, get_incidents

import requests
import os
from datetime import datetime

# Configure logger
logger = logging.getLogger("alerting")
logger.setLevel(logging.INFO)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Email Alert Delivery ---

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "alert@example.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "password")
EMAIL_FROM = os.getenv("EMAIL_FROM", "alert@example.com")
EMAIL_TO = os.getenv("EMAIL_TO", "devops@example.com")  # Comma-separated list

def send_email_alert(subject: str, body: str, recipients: Optional[List[str]] = None) -> bool:
    """
    Sends an email alert using SMTP.
    """
    recipients = recipients or EMAIL_TO.split(",")
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_FROM, recipients, msg.as_string())
        logger.info(f"Email alert sent to {recipients}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")
        return False

# --- Slack Alert Delivery ---

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

def send_slack_alert(message: str) -> bool:
    """
    Sends an alert message to Slack via webhook.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("Slack webhook URL not configured.")
        return False
    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info("Slack alert sent successfully.")
            return True
        else:
            logger.error(f"Slack alert failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False

# --- Alert Generation & Logging ---

def log_alert_event(
    db: Session,
    alert: Alert,
    event_type: str,
    actor: Optional[str] = "system",
    details: Optional[dict] = None,
    incident: Optional[Incident] = None,
) -> AuditLog:
    """
    Logs an alert event to the immutable audit log.
    """
    audit_log = AuditLog(
        incident_id=incident.id if incident else alert.incident_id,
        alert_id=alert.id,
        event_type=event_type,
        event_time=datetime.utcnow(),
        actor=actor,
        details=details or {},
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    logger.info(f"Audit log event recorded: {event_type} for alert {alert.id}")
    return audit_log

def deliver_alert(db: Session, alert: Alert, incident: Optional[Incident] = None) -> bool:
    """
    Delivers an alert via configured channels and logs the event.
    """
    subject = f"[{alert.severity.upper()}] Alert: {alert.title}"
    body = f"""
    Alert Type: {alert.type}
    Resource ID: {alert.resource_id}
    Triggered At: {alert.triggered_at}
    Severity: {alert.severity}
    Description: {alert.description}
    Details: {alert.details}
    """
    slack_message = f"*{subject}*\n{body}"

    email_sent = send_email_alert(subject, body)
    slack_sent = send_slack_alert(slack_message)

    log_alert_event(
        db=db,
        alert=alert,
        event_type="alert_generated",
        details={
            "email_sent": email_sent,
            "slack_sent": slack_sent,
        },
        incident=incident,
    )
    return email_sent or slack_sent

def resolve_alert(db: Session, alert: Alert, actor: Optional[str] = "system") -> Alert:
    """
    Resolves an alert and logs the resolution event.
    """
    if alert.status == AlertStatus.RESOLVED:
        logger.info(f"Alert already resolved: {alert.id}")
        return alert
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    log_alert_event(
        db=db,
        alert=alert,
        event_type="alert_resolved",
        actor=actor,
        details={"resolved_at": alert.resolved_at},
    )
    logger.info(f"Alert resolved: {alert.id}")
    return alert

# --- FastAPI Router ---

from pydantic import BaseModel, Field

class AlertOut(BaseModel):
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

alerting_router = APIRouter()

@alerting_router.post("/alerts/{alert_id}/deliver", status_code=status.HTTP_200_OK)
def deliver_alert_endpoint(alert_id: UUID, db: Session = Depends(get_db)):
    """
    Deliver an alert via email and Slack, and log the event.
    """
    alert = get_alert(db, alert_id)
    incident = None
    if alert.incident_id:
        incident = get_incident(db, alert.incident_id)
    success = deliver_alert(db, alert, incident)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deliver alert via any channel."
        )
    return {"detail": "Alert delivered successfully."}

@alerting_router.post("/alerts/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert_endpoint(alert_id: UUID, actor: Optional[str] = Query("system"), db: Session = Depends(get_db)):
    """
    Resolve an alert and log the resolution event.
    """
    alert = get_alert(db, alert_id)
    resolved_alert = resolve_alert(db, alert, actor=actor)
    return resolved_alert

@alerting_router.get("/alerts/", response_model=List[AlertOut])
def list_alerts(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """
    List all alerts.
    """
    alerts = get_alerts(db, skip=skip, limit=limit)
    return alerts

@alerting_router.get("/alerts/{alert_id}", response_model=AlertOut)
def get_alert_endpoint(alert_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific alert.
    """
    alert = get_alert(db, alert_id)
    return alert

# Exported symbols
__all__ = [
    "alerting_router",
    "deliver_alert",
    "resolve_alert",
    "send_email_alert",
    "send_slack_alert",
    "log_alert_event",
]