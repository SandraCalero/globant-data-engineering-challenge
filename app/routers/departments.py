from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select
import logging

from ..models import Department, BatchResponse
from ..services import DatabaseService
from ..db import SessionDep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/departments/batch", response_model=BatchResponse, status_code=status.HTTP_201_CREATED, tags=["departments"])
async def batch_upsert_departments(session: SessionDep):
    """
    Batch upsert departments from CSV files in S3 into the database.
    Creates or updates department records in bulk.
    """
    try:
        return DatabaseService.batch_upsert(session, Department)

    except Exception as e:
        logger.error(f"Error processing departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/departments", response_model=list[Department], tags=["departments"])
async def list_departments(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    List departments with pagination.
    """
    offset = (page - 1) * limit
    statement = select(Department).order_by(
        Department.id).offset(offset).limit(limit)
    results = session.exec(statement)
    departments = results.all()
    return departments
