from .routers import departments, health_checks
from .routers import departments, employees, health_checks, jobs, all_tables, metrics
from fastapi import FastAPI
import os


# Create FastAPI app
app = FastAPI()

app.include_router(health_checks.router)
app.include_router(departments.router)
app.include_router(jobs.router)
app.include_router(employees.router)
app.include_router(all_tables.router)
app.include_router(metrics.router)


@app.get("/")
async def root():
    """
    Root endpoint for the Globant Data Engineering API.
    Returns API metadata and available endpoints.
    """
    return {"message": "Globant Data Engineering API",
            "version": "1.0.0",
            "env": os.getenv("ENV"),
            "s3_bucket": os.getenv("S3_BUCKET_NAME"),
            "endpoints": {
                "health_db_check": "/health-db",
                "health_s3_check": "/health-s3",
                "departments": "/departments",
                "jobs": "/jobs",
                "employees": "/employees",
                "all_tables": "/all-tables",
                "metrics": {
                    "hired_by_quarter_2021": "/metrics/hired-by-quarter-2021",
                    "top_hiring_departments": "/metrics/top-hiring-departments"
                }
            }
            }
