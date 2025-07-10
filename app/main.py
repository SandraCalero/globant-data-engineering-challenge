from app.routers import departments, employees, health_checks, jobs
from fastapi import FastAPI
import os

from .routers import departments, health_checks

# Create FastAPI app
app = FastAPI(title="Globant Data Engineering API",
              description="REST API for CSV data migration and batch processing on AWS",
              version="1.0.0")

app.include_router(health_checks.router)
app.include_router(departments.router)
app.include_router(jobs.router)
app.include_router(employees.router)


@app.get("/")
async def root():
    return {"message": "Globant Data Engineering API",
            "version": "1.0.0",
            "env": os.getenv("ENV"),
            "s3_bucket": os.getenv("S3_BUCKET_NAME"),
            "endpoints": {
                "health_db_check": "/health-db",
                "health_s3_check": "/health-s3",
                "departments": "/departments",
                "jobs": "/jobs",
                "employees": "/employees"
            }
            }
