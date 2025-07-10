from datetime import datetime
from sqlmodel import SQLModel, Field


class DepartmentBase(SQLModel):
    """Base model for Department entity"""
    id: int | None = Field(default=None, primary_key=True)
    department: str = Field(default=None)


class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass


class Department(DepartmentBase, table=True):
    """Model for Department entity"""
    pass


class JobBase(SQLModel):
    """Base model for Job entity"""
    id: int | None = Field(default=None, primary_key=True)
    job: str = Field(default=None)


class JobCreate(JobBase):
    """Model for creating a new job"""
    pass


class Job(JobBase, table=True):
    """Model for Job entity"""
    pass


class EmployeeBase(SQLModel):
    """Base model for Employee entity"""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    hire_date: datetime = Field(default=None)
    department_id: int = Field(default=None, foreign_key="department.id")
    job_id: int = Field(default=None, foreign_key="job.id")


class EmployeeCrate(EmployeeBase):
    """Model for creating a new employee"""
    pass


class Employee(EmployeeBase, table=True):
    """Model for Employee entity"""
    pass


class HealthResponse(SQLModel):
    status: str
    database_connected: bool


class S3HealthResponse(SQLModel):
    status: str
    s3_connected: bool
    files_count: int | None = None
    files: list[dict] | None = None
    error: str | None = None
