from fastapi import APIRouter, HTTPException, Query
import logging
from sqlmodel import select

from ..db import SessionDep
from ..models import VHiredByQuarter2021, VTopHiringDepartments, MetricsResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics/hired-by-quarter-2021", response_model=MetricsResponse, tags=["metrics"])
async def hired_by_quarter_2021(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    Number of employees hired for each position and department in 2021 divided by quarter.
    """
    offset = (page - 1) * limit
    try:
        statement = select(VHiredByQuarter2021).offset(offset).limit(limit)
        result = session.exec(statement)
        rows = result.all()

        output = [
            {
                "department": row.department,
                "job": row.job,
                "Q1": row.q1,
                "Q2": row.q2,
                "Q3": row.q3,
                "Q4": row.q4
            }
            for row in rows
        ]

        return MetricsResponse(page=page, limit=limit, count=len(output), data=output)

    except Exception as e:
        logger.error(f"Error in hired_by_quarter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/top-hiring-departments", response_model=MetricsResponse, tags=["metrics"])
async def top_hiring_departments(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    List of ids, names and number of employees hired for each department that hired more employees than the average in 2021.
    """
    try:
        offset = (page - 1) * limit
        statement = select(VTopHiringDepartments).offset(offset).limit(limit)
        result = session.exec(statement)
        rows = result.all()

        output = [
            {
                "id": row.id,
                "department": row.department,
                "employees_hired": row.employees_hired
            }
            for row in rows
        ]

        return MetricsResponse(page=page, limit=limit, count=len(output), data=output)

    except Exception as e:
        logger.error(f"Error in top_hiring_departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
