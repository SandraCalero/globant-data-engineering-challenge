from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

class DepartmentBase(SQLModel):
    """Base model for Department entity"""
    id: int | None = Field(default=None, primary_key=True)
    department: str = Field(default=None)

class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass

class JobBase(SQLModel):
    """Base model for Job entity"""
    id: int | None = Field(default=None, primary_key=True)
    job: str = Field(default=None)

class JobCreate(JobBase):
    """Model for creating a new job"""
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
