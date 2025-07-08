from fastapi import FastAPI
import os
import logging
from sqlmodel import select
from .models import DepartmentBase, DepartmentCreate, JobBase, JobCreate, EmployeeBase, EmployeeCrate, HealthResponse, S3HealthResponse
from .db import SessionDep
from .services import S3Service


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Globant Data Engineering API",
description="REST API for CSV data migration and batch processing on AWS",
version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Globant Data Engineering API",
            "version": "1.0.0",
            "env": os.getenv("ENV"),
            "s3_bucket": os.getenv("S3_BUCKET_NAME"),
            "endpoints": {
                "health_db_check": "/health-db",
                "get_stats": "/stats",
                "departments": "/departments",
                "jobs": "/jobs",
                "employees": "/employees"
            }
        }

@app.get("/health-db", response_model=HealthResponse)
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

@app.get("/health-s3", response_model=S3HealthResponse)
async def health_s3_check():
    """Health check S3 bucket connection"""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_connected = False
    files = None
    files_count = None
    error = None
    try:
        files = S3Service.read_s3_files(bucket_name, prefix="")
        s3_connected = True
        files_count = len(files)
    except Exception as e:
        logger.error(f"S3 connection failed: {e}")
        error = str(e)
    return S3HealthResponse(
        status="healthy" if s3_connected else "unhealthy",
        s3_connected=s3_connected,
        files_count=files_count,
        files=[{"key": f["key"], "size": f["size"]} for f in files] if files else None,
        error=error
    )


departments = []

@app.post("/departments", response_model=DepartmentBase)
async def create_department(department_data: DepartmentCreate, session: SessionDep):
    department = DepartmentBase.model_validate(department_data.model_dump())
    departments.append(department)
    return department

@app.get("/departments", response_model=list[DepartmentBase])
async def list_customer():
    return departments

@app.post("/jobs", response_model=JobBase)
async def create_job(job_data: JobCreate):
    job = JobBase.model_validate(job_data.model_dump())
    return job

@app.post("/employees", response_model=EmployeeBase)
async def create_employee(employee_data: EmployeeCrate):
    employee = EmployeeBase.model_validate(employee_data.model_dump())
    return employee


