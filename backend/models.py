from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
    Enum,
    create_engine,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

# SQLAlchemy base class
Base = declarative_base()

# Database engine (to be configured via environment or settings)
engine = create_engine(
    "postgresql+psycopg2://user:password@localhost:5432/cloud_monitoring",
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Enums for Alert and Incident status/types
class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"

class AlertType(str, enum.Enum):
    RESOURCE = "resource"
    SECURITY = "security"
    MISCONFIGURATION = "misconfiguration"

class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Product model (CRUD operations required)
class Product(Base):
    """
    Represents a product entity for which resources may be provisioned.
    """
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    resources = relationship("Resource", back_populates="product", cascade="all, delete-orphan")

# Cloud Resource model
class Resource(Base):
    """
    Represents a provisioned cloud resource (VM, DB, storage, etc.).
    """
    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint('cloud_id', 'cloud_provider', name='uq_resource_cloud_id_provider'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(128), nullable=False)
    cloud_id = Column(String(128), nullable=False)  # Cloud provider's resource ID
    cloud_provider = Column(String(32), nullable=False)  # e.g., aws, azure, gcp
    resource_type = Column(String(64), nullable=False)  # e.g., EC2, S3, VM, SQLDatabase
    metadata = Column(JSON, nullable=True)  # Additional resource metadata
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="resources")
    alerts = relationship("Alert", back_populates="resource", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="resource", cascade="all, delete-orphan")

# Alert model
class Alert(Base):
    """
    Represents an alert generated for a resource or security event.
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=True)
    type = Column(Enum(AlertType), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    severity = Column(String(16), nullable=False)  # e.g., critical, warning, info
    details = Column(JSON, nullable=True)  # Additional alert details (e.g., metric values)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)

    resource = relationship("Resource", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")

# Incident model
class Incident(Base):
    """
    Represents an incident (group of alerts or a major event).
    """
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    created_by = Column(String(64), nullable=True)  # User or system

    resource = relationship("Resource", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="incident", cascade="all, delete-orphan")

# Audit Log model (immutable)
class AuditLog(Base):
    """
    Immutable audit log for alert generation, resolution, and security events.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(64), nullable=False)  # e.g., alert_generated, alert_resolved, security_event
    event_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor = Column(String(64), nullable=True)  # User or system
    details = Column(JSON, nullable=True)  # Additional event details

    incident = relationship("Incident", back_populates="audit_logs")
    alert = relationship("Alert")

# Exported symbols
__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "Product",
    "Resource",
    "Alert",
    "Incident",
    "AuditLog",
    "AlertStatus",
    "AlertType",
    "IncidentStatus",
]