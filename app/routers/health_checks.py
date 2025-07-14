from fastapi import APIRouter
from sqlmodel import select
import logging

from ..models import HealthResponse, S3HealthResponse
from ..services import S3Service
from ..db import SessionDep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health-db", response_model=HealthResponse, tags=["health checks"])
async def health_db_check(session: SessionDep):
    """Health check database connection"""
    try:
        # Test database connection
        session.exec(select(1))
        database_connected = True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        database_connected = False

    return HealthResponse(
        status="healthy" if database_connected else "unhealthy",
        database_connected=database_connected
    )


@router.get("/health-s3", response_model=S3HealthResponse, tags=["health checks"])
def health_s3_check():
    """Health check S3 bucket connection"""
    s3_connected = False
    error = None
    try:
        bucket_name = S3Service.get_and_validate_s3_bucket_name()
        s3_connected = True
    except Exception as e:
        logger.error(f"S3 connection failed: {e}")
        error = str(e)
    return S3HealthResponse(
        status="healthy" if s3_connected else "unhealthy",
        s3_connected=s3_connected,
        bucket_name=bucket_name if s3_connected else None,
        error=error
    )
