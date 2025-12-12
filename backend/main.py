import logging
import sys
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import Base, engine
from crud import (
    get_products_router,
    get_resources_router,
    get_alerts_router,
    get_incidents_router,
)
from monitoring import monitoring_router
from alerting import alerting_router
from security_events import security_events_router
from audit_log import audit_log_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cloud-monitoring-api")

# Initialize FastAPI app
app = FastAPI(
    title="Cloud Resource Monitoring & Alerting System",
    description="Proactive monitoring, alerting, and incident management for cloud resources.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables if not exist
@app.on_event("startup")
def on_startup():
    logger.info("Starting up Cloud Resource Monitoring & Alerting System API...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured.")
    except SQLAlchemyError as e:
        logger.error(f"Database initialization error: {e}")
        raise

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTPException: {exc.detail} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred."}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."}
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint for readiness/liveness probes.
    """
    return {"status": "ok"}

# Include routers from modules
app.include_router(get_products_router(), prefix="/products", tags=["Products"])
app.include_router(get_resources_router(), prefix="/resources", tags=["Resources"])
app.include_router(get_alerts_router(), prefix="/alerts", tags=["Alerts"])
app.include_router(get_incidents_router(), prefix="/incidents", tags=["Incidents"])
app.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(alerting_router, prefix="/alerting", tags=["Alerting"])
app.include_router(security_events_router, prefix="/security-events", tags=["Security Events"])
app.include_router(audit_log_router, prefix="/audit-log", tags=["Audit Log"])

# Export FastAPI app for ASGI server
__all__ = ["app"]