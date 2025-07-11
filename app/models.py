from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class DepartmentBase(SQLModel):
    """Base model for Department entity"""
    id: int | None = Field(default=None, primary_key=True)
    department: str = Field(default=None)


class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass


class Department(DepartmentBase, table=True):
    """Model for Department entity"""
    employees: list["Employee"] = Relationship(back_populates="department")


class JobBase(SQLModel):
    """Base model for Job entity"""
    id: int | None = Field(default=None, primary_key=True)
    job: str = Field(default=None)


class JobCreate(JobBase):
    """Model for creating a new job"""
    pass


class Job(JobBase, table=True):
    """Model for Job entity"""
    employees: list["Employee"] = Relationship(back_populates="job")


class EmployeeBase(SQLModel):
    """Base model for Employee entity"""
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(default=None)
    hire_date: datetime | None = Field(default=None)
    department_id: int | None = Field(
        default=None, foreign_key="department.id")
    job_id: int | None = Field(default=None, foreign_key="job.id")


class EmployeeCrate(EmployeeBase):
    """Model for creating a new employee"""
    pass


class Employee(EmployeeBase, table=True):
    """Model for Employee entity"""
    department: Department = Relationship(back_populates="employees")
    job: Job = Relationship(back_populates="employees")


class HealthResponse(SQLModel):
    status: str
    database_connected: bool


class S3HealthResponse(SQLModel):
    status: str
    s3_connected: bool
    files_count: int | None = None
    files: list[dict] | None = None
    error: str | None = None


class BatchResponse(SQLModel):
    table: str
    total: int
    inserted: int
    updated: int
    failed: int
    errors:  list[dict] = []
    file_not_found: bool | None = None
