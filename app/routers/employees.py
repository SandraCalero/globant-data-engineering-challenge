from fastapi import APIRouter, status, HTTPException, Query
from sqlmodel import select
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
    """
    Batch upsert employees from CSV files in S3 into the database.
    Creates or updates employee records in bulk.
    """
    try:
        return DatabaseService.batch_upsert(session, Employee)

    except Exception as e:
        logger.error(f"Error processing employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employees", response_model=list[Employee], tags=["employees"])
async def list_employees(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    List employees with pagination.
    """
    offset = (page - 1) * limit
    statement = select(Employee).order_by(
        Employee.id).offset(offset).limit(limit)
    results = session.exec(statement)
    employees = results.all()
    return employees
