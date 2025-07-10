from fastapi import APIRouter
from sqlmodel import select
import os
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
async def health_s3_check():
    """Health check S3 bucket connection"""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_connected = False
    files = None
    files_count = None
    error = None
    try:
        files = S3Service.list_csv_files(bucket_name)
        s3_connected = True
        files_count = len(files)
    except Exception as e:
        logger.error(f"S3 connection failed: {e}")
        error = str(e)
    return S3HealthResponse(
        status="healthy" if s3_connected else "unhealthy",
        s3_connected=s3_connected,
        files_count=files_count,
        files=[{"key": f} for f in files] if files else None,
        error=error
    )
