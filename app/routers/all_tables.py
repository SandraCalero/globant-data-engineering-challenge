from fastapi import APIRouter, status, HTTPException
import logging

from ..models import Department, Employee, Job, BatchResponse
from ..services import DatabaseService
from ..db import SessionDep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Order matters: Department and Job must be processed before Employee due to foreign key relationships
MODEL_MAP = {
    "Department": Department,
    "Job": Job,
    "Employee": Employee
}


@router.post("/all-tables/batch", response_model=list[BatchResponse], status_code=status.HTTP_201_CREATED, tags=["all-tables"])
async def batch_upsert_all_tables(session: SessionDep):
    """
    Process all CSV files and upsert data into all tables.
    Processes departments.csv, jobs.csv, and hired_employees.csv in sequence.
    """
    try:
        return [DatabaseService.batch_upsert(session, model_class) for _, model_class in MODEL_MAP.items()]

    except Exception as e:
        logger.error(f"Error processing all tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))
