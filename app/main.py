from datetime import datetime
from fastapi import FastAPI, HTTPException
from .models import DepartmentBase, DepartmentCreate, JobBase, JobCreate, EmployeeBase, EmployeeCrate
from .db import SessionDep
from .s3_utils import read_s3_files

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

departments = []

@app.post("/departments", response_model=DepartmentBase)
async def create_department(department_data: DepartmentCreate):
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

@app.get("/test-s3")
async def test_s3_files(bucket_name: str, prefix: str = ""):
    """
    Endpoint to test the read_s3_files function
    Parameters:
    - bucket_name: S3 bucket name
    - prefix: Optional prefix to filter files
    """
    try:
        files_data = read_s3_files(bucket_name, prefix)
        
        return {
            "success": True,
            "message": f"Processed {len(files_data)} files",
            "files_count": len(files_data),
            "files": [
                {
                    "key": file_data["key"],
                    "size": file_data["size"],
                    "content_length": len(file_data["content"]),
                    "content_preview": file_data["content"][:200] + "..." if len(file_data["content"]) > 200 else file_data["content"]
                }
                for file_data in files_data
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading files from S3: {str(e)}"
        )