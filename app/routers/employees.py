from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select
import os
import logging

from ..models import Employee, BatchResponse
from ..services import DatabaseService
from ..db import SessionDep
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/employees/batch", response_model=BatchResponse, status_code=status.HTTP_201_CREATED, tags=["employees"])
async def batch_upsert_employees(session: SessionDep):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="S3_BUCKET_NAME environment variable not set")

    result = DatabaseService.batch_upsert(bucket_name, session, Employee)
    return result


@router.get("/employees", response_model=list[Employee], tags=["employees"])
async def list_employees(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    offset = (page - 1) * limit
    statement = select(Employee).order_by(
        Employee.id).offset(offset).limit(limit)
    results = session.exec(statement)
    employees = results.all()
    return employees
