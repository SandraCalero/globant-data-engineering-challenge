from fastapi import APIRouter, status, HTTPException
import os
import logging

from ..models import Department, Employee, Job, BatchResponse
from ..services import DatabaseService, S3Service
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
    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="S3_BUCKET_NAME environment variable not set")

    # Define the tables to process with their corresponding CSV files and models
    results = []
    for _, model_class in MODEL_MAP.items():
        # Process the CSV file and upsert data into the table
        result = DatabaseService.batch_upsert(
            session=session, bucket_name=bucket_name, model_class=model_class)
        results.append(result)

    return results
