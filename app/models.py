from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class DepartmentBase(SQLModel):
    """Base model for Department entity"""
    id: int | None = Field(default=None, primary_key=True)
    department: str = Field(default=None)


class Department(DepartmentBase, table=True):
    """Model for Department entity"""
    employees: list["Employee"] = Relationship(back_populates="department")


class JobBase(SQLModel):
    """Base model for Job entity"""
    id: int | None = Field(default=None, primary_key=True)
    job: str = Field(default=None)


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


class Employee(EmployeeBase, table=True):
    """Model for Employee entity"""
    department: Department = Relationship(back_populates="employees")
    job: Job = Relationship(back_populates="employees")


class HealthResponse(SQLModel):
    """Model for health check database response."""
    status: str
    database_connected: bool


class S3HealthResponse(SQLModel):
    """Model for health check S3 response."""
    status: str
    s3_connected: bool
    bucket_name: str | None = None
    error: str | None = None


class BatchResponse(SQLModel):
    """Model for batch processing response."""
    table: str | None = None
    total: int
    inserted: int
    updated: int
    failed: int
    errors:  list[dict] = []
    processed_files: list[str] | None = None


# View Models for Metrics
class VHiredByQuarter2021(SQLModel, table=True):
    """Model for VHiredByQuarter2021 view"""
    department: str = Field(default=None, primary_key=True)
    job: str = Field(default=None, primary_key=True)
    q1: int = Field(default=None)
    q2: int = Field(default=None)
    q3: int = Field(default=None)
    q4: int = Field(default=None)


class VTopHiringDepartments(SQLModel, table=True):
    """Model for VTopHiringDepartments view"""
    id: int = Field(primary_key=True)
    department: str = Field(default=None)
    employees_hired: int = Field(default=None)


class MetricsResponse(SQLModel):
    """Model for Metrics response"""
    page: int = 1
    limit: int = 10
    count: int
    data: list[dict]
