from fastapi import APIRouter, status, HTTPException
from sqlmodel import select
import os
import logging

from ..models import Job
from ..services import DatabaseService
from ..db import SessionDep
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/jobs/batch", status_code=status.HTTP_201_CREATED, tags=["jobs"])
async def batch_upsert_jobs(session: SessionDep):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="S3_BUCKET_NAME environment variable not set")

    result = DatabaseService.batch_upsert(
        "jobs", bucket_name, "jobs.csv", session, Job)
    return result


@router.get("/jobs", response_model=list[Job], tags=["jobs"])
async def list_jobs(session: SessionDep):
    return session.exec(select(Job)).all()
