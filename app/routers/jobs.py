from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select
import logging

from ..models import Job, BatchResponse
from ..services import DatabaseService
from ..db import SessionDep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/jobs/batch", response_model=BatchResponse, status_code=status.HTTP_201_CREATED, tags=["jobs"])
async def batch_upsert_jobs(session: SessionDep):
    """
    Batch upsert jobs from CSV files in S3 into the database.
    Creates or updates job records in bulk.
    """
    try:
        return DatabaseService.batch_upsert(session, Job)

    except Exception as e:
        logger.error(f"Error processing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=list[Job], tags=["jobs"])
async def list_jobs(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    List jobs with pagination.
    """
    offset = (page - 1) * limit
    statement = select(Job).order_by(
        Job.id).offset(offset).limit(limit)
    results = session.exec(statement)
    jobs = results.all()
    return jobs
