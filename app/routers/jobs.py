from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select
import os
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
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="S3_BUCKET_NAME environment variable not set")

    result = DatabaseService.batch_upsert(bucket_name, session, Job)
    return result


@router.get("/jobs", response_model=list[Job], tags=["jobs"])
async def list_jobs(session: SessionDep, page: int = 1, limit: int = Query(10, le=100)):
    offset = (page - 1) * limit
    statement = select(Job).order_by(
        Job.id).offset(offset).limit(limit)
    results = session.exec(statement)
    jobs = results.all()
    return jobs
