from fastapi import APIRouter, status, HTTPException
from sqlmodel import select
import os
import logging

from ..models import Department
from ..services import DatabaseService
from ..db import SessionDep
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/departments/batch", status_code=status.HTTP_201_CREATED, tags=["departments"])
async def batch_upsert_departments(session: SessionDep):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="S3_BUCKET_NAME environment variable not set")

    result = DatabaseService.batch_upsert(
        "departments", bucket_name, "departments.csv", session, Department)
    return result


@router.get("/departments", response_model=list[Department], tags=["departments"])
async def list_departments(session: SessionDep):
    return session.exec(select(Department)).all()
