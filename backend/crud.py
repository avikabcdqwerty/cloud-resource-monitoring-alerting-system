import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    Product,
    Resource,
    Alert,
    Incident,
    AuditLog,
)

# Configure logger for CRUD operations
logger = logging.getLogger("crud")
logger.setLevel(logging.INFO)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- Product CRUD Operations --------------------

def create_product(db: Session, name: str, description: Optional[str] = None) -> Product:
    """
    Create a new product.
    """
    existing = db.query(Product).filter(Product.name == name).first()
    if existing:
        logger.warning(f"Attempt to create duplicate product: {name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name already exists."
        )
    product = Product(name=name, description=description)
    db.add(product)
    db.commit()
    db.refresh(product)
    logger.info(f"Product created: {product.id} ({product.name})")
    return product

def get_product(db: Session, product_id: UUID) -> Product:
    """
    Retrieve a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    return product

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """
    Retrieve a list of products.
    """
    return db.query(Product).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: UUID, name: Optional[str] = None, description: Optional[str] = None) -> Product:
    """
    Update an existing product.
    """
    product = get_product(db, product_id)
    if name:
        # Check for name conflict
        existing = db.query(Product).filter(Product.name == name, Product.id != product_id).first()
        if existing:
            logger.warning(f"Attempt to update product to duplicate name: {name}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another product with this name already exists."
            )
        product.name = name
    if description is not None:
        product.description = description
    db.commit()
    db.refresh(product)
    logger.info(f"Product updated: {product.id} ({product.name})")
    return product

def delete_product(db: Session, product_id: UUID) -> None:
    """
    Delete a product by its ID.
    """
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
    logger.info(f"Product deleted: {product.id} ({product.name})")

# -------------------- Resource CRUD Operations --------------------

def get_resource(db: Session, resource_id: UUID) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        logger.warning(f"Resource not found: {resource_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found."
        )
    return resource

def get_resources(db: Session, skip: int = 0, limit: int = 100) -> List[Resource]:
    return db.query(Resource).order_by(Resource.created_at.desc()).offset(skip).limit(limit).all()

# -------------------- Alert CRUD Operations --------------------

def get_alert(db: Session, alert_id: UUID) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        logger.warning(f"Alert not found: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found."
        )
    return alert

def get_alerts(db: Session, skip: int = 0, limit: int = 100) -> List[Alert]:
    return db.query(Alert).order_by(Alert.triggered_at.desc()).offset(skip).limit(limit).all()

# -------------------- Incident CRUD Operations --------------------

def get_incident(db: Session, incident_id: UUID) -> Incident:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        logger.warning(f"Incident not found: {incident_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found."
        )
    return incident

def get_incidents(db: Session, skip: int = 0, limit: int = 100) -> List[Incident]:
    return db.query(Incident).order_by(Incident.opened_at.desc()).offset(skip).limit(limit).all()

# -------------------- Routers for FastAPI --------------------

from fastapi import Body
from pydantic import BaseModel, Field

# Pydantic schemas for Product
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = Field(None, max_length=1024)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=1024)

class ProductOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

# Product Router
def get_products_router() -> APIRouter:
    router = APIRouter()

    @router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
    def create(product: ProductCreate, db: Session = Depends(get_db)):
        return create_product(db, name=product.name, description=product.description)

    @router.get("/", response_model=List[ProductOut])
    def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return get_products(db, skip=skip, limit=limit)

    @router.get("/{product_id}", response_model=ProductOut)
    def get(product_id: UUID, db: Session = Depends(get_db)):
        return get_product(db, product_id)

    @router.put("/{product_id}", response_model=ProductOut)
    def update(product_id: UUID, product: ProductUpdate, db: Session = Depends(get_db)):
        return update_product(db, product_id, name=product.name, description=product.description)

    @router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(product_id: UUID, db: Session = Depends(get_db)):
        delete_product(db, product_id)
        return

    return router

# Resource Router (read-only for now)
def get_resources_router() -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=List[dict])
    def list_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        resources = get_resources(db, skip=skip, limit=limit)
        # Return as dicts for now; can define Pydantic schemas as needed
        return [r.__dict__ for r in resources]

    @router.get("/{resource_id}", response_model=dict)
    def get(resource_id: UUID, db: Session = Depends(get_db)):
        resource = get_resource(db, resource_id)
        return resource.__dict__

    return router

# Alert Router (read-only for now)
def get_alerts_router() -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=List[dict])
    def list_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        alerts = get_alerts(db, skip=skip, limit=limit)
        return [a.__dict__ for a in alerts]

    @router.get("/{alert_id}", response_model=dict)
    def get(alert_id: UUID, db: Session = Depends(get_db)):
        alert = get_alert(db, alert_id)
        return alert.__dict__

    return router

# Incident Router (read-only for now)
def get_incidents_router() -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=List[dict])
    def list_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        incidents = get_incidents(db, skip=skip, limit=limit)
        return [i.__dict__ for i in incidents]

    @router.get("/{incident_id}", response_model=dict)
    def get(incident_id: UUID, db: Session = Depends(get_db)):
        incident = get_incident(db, incident_id)
        return incident.__dict__

    return router

# Exported symbols
__all__ = [
    "get_db",
    "create_product",
    "get_product",
    "get_products",
    "update_product",
    "delete_product",
    "get_resource",
    "get_resources",
    "get_alert",
    "get_alerts",
    "get_incident",
    "get_incidents",
    "get_products_router",
    "get_resources_router",
    "get_alerts_router",
    "get_incidents_router",
]