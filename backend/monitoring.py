import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from models import (
    SessionLocal,
    Resource,
    Alert,
    AlertStatus,
    AlertType,
)
from crud import get_resource, get_resources

# For demonstration, we use boto3 for AWS CloudWatch integration.
# In production, credentials and region should be securely managed.
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Configure logger
logger = logging.getLogger("monitoring")
logger.setLevel(logging.INFO)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Supported metrics for demonstration
SUPPORTED_METRICS = ["CPUUtilization", "MemoryUtilization", "NetworkIn", "NetworkOut", "DiskReadBytes", "DiskWriteBytes"]

# Example: Metric thresholds (could be stored in DB/config)
DEFAULT_THRESHOLDS = {
    "CPUUtilization": 80.0,  # percent
    "MemoryUtilization": 80.0,  # percent
    "NetworkIn": 1000000000,  # bytes
    "NetworkOut": 1000000000,  # bytes
    "DiskReadBytes": 1000000000,  # bytes
    "DiskWriteBytes": 1000000000,  # bytes
}

# --- CloudWatch Integration ---

def get_cloudwatch_client(region_name: str = "us-east-1"):
    """
    Returns a boto3 CloudWatch client.
    """
    try:
        client = boto3.client("cloudwatch", region_name=region_name)
        return client
    except Exception as e:
        logger.error(f"Failed to create CloudWatch client: {e}")
        raise

def fetch_aws_metrics(resource: Resource, metrics: List[str]) -> Dict[str, Any]:
    """
    Fetches specified metrics for a given AWS resource from CloudWatch.
    """
    client = get_cloudwatch_client()
    results = {}
    for metric in metrics:
        try:
            # For demonstration, assume EC2 instance
            response = client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName=metric,
                Dimensions=[
                    {"Name": "InstanceId", "Value": resource.cloud_id}
                ],
                StartTime=datetime.utcnow().replace(microsecond=0),
                EndTime=datetime.utcnow().replace(microsecond=0),
                Period=300,
                Statistics=["Average"],
            )
            datapoints = response.get("Datapoints", [])
            value = datapoints[-1]["Average"] if datapoints else None
            results[metric] = value
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error fetching metric {metric} for resource {resource.cloud_id}: {e}")
            results[metric] = None
    return results

# --- Metric Evaluation ---

def evaluate_metrics(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Evaluates metrics against thresholds and returns a list of breaches.
    """
    breaches = []
    for metric, value in metrics.items():
        threshold = thresholds.get(metric)
        if threshold is not None and value is not None and value > threshold:
            breaches.append({
                "metric": metric,
                "value": value,
                "threshold": threshold,
            })
    return breaches

# --- Monitoring Logic ---

def collect_and_evaluate_metrics_for_resource(db: Session, resource: Resource) -> Dict[str, Any]:
    """
    Collects metrics for a resource and evaluates them against thresholds.
    Returns a dict with metrics and any breaches.
    """
    if not resource.monitoring_enabled:
        logger.info(f"Monitoring disabled for resource {resource.id}")
        return {"metrics": {}, "breaches": []}

    # For demonstration, only AWS EC2 supported
    if resource.cloud_provider.lower() == "aws" and resource.resource_type.lower() == "ec2":
        metrics = fetch_aws_metrics(resource, SUPPORTED_METRICS)
    else:
        logger.warning(f"Monitoring not implemented for provider/type: {resource.cloud_provider}/{resource.resource_type}")
        metrics = {}

    breaches = evaluate_metrics(metrics, DEFAULT_THRESHOLDS)
    return {"metrics": metrics, "breaches": breaches}

# --- FastAPI Router ---

from pydantic import BaseModel, Field

class MetricResult(BaseModel):
    metric: str
    value: Optional[float]
    threshold: Optional[float]

class ResourceMetricsOut(BaseModel):
    resource_id: UUID
    metrics: Dict[str, Optional[float]]
    breaches: List[MetricResult]

monitoring_router = APIRouter()

@monitoring_router.get("/resources/{resource_id}/metrics", response_model=ResourceMetricsOut)
def get_resource_metrics(
    resource_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Collect and evaluate metrics for a specific resource.
    """
    resource = get_resource(db, resource_id)
    result = collect_and_evaluate_metrics_for_resource(db, resource)
    return ResourceMetricsOut(
        resource_id=resource_id,
        metrics=result["metrics"],
        breaches=[
            MetricResult(
                metric=breach["metric"],
                value=breach["value"],
                threshold=breach["threshold"]
            ) for breach in result["breaches"]
        ]
    )

@monitoring_router.get("/resources/metrics", response_model=List[ResourceMetricsOut])
def get_all_resources_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Collect and evaluate metrics for all resources.
    """
    resources = get_resources(db, skip=skip, limit=limit)
    results = []
    for resource in resources:
        result = collect_and_evaluate_metrics_for_resource(db, resource)
        results.append(ResourceMetricsOut(
            resource_id=resource.id,
            metrics=result["metrics"],
            breaches=[
                MetricResult(
                    metric=breach["metric"],
                    value=breach["value"],
                    threshold=breach["threshold"]
                ) for breach in result["breaches"]
            ]
        ))
    return results

# Exported symbols
__all__ = [
    "monitoring_router",
    "collect_and_evaluate_metrics_for_resource",
    "evaluate_metrics",
    "fetch_aws_metrics",
    "get_cloudwatch_client",
    "SUPPORTED_METRICS",
    "DEFAULT_THRESHOLDS",
]