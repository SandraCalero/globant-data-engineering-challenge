from fastapi import APIRouter, status, HTTPException, Depends, Query
import os
import logging
from sqlmodel import select

from ..db import SessionDep
from ..models import VHiredByQuarter2021, VTopHiringDepartments

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics/hired-by-quarter-2021", tags=["metrics"])
async def hired_by_quarter_2021(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    Number of employees hired for each position and department in 2021 divided by quarter.
    """
    offset = (page - 1) * limit
    try:
        # Use SQLModel with the view
        statement = select(VHiredByQuarter2021).offset(offset).limit(limit)
        result = session.exec(statement)
        rows = result.all()

        # Convert to JSON format
        output = []
        for row in rows:
            output.append({
                "department": row.department,
                "job": row.job,
                "Q1": row.q1,
                "Q2": row.q2,
                "Q3": row.q3,
                "Q4": row.q4
            })

        # Return response with pagination metadata
        return {
            "page": page,
            "limit": limit,
            "count": len(output),
            "data": output
        }

    except Exception as e:
        logger.error(f"Error in hired_by_quarter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/top-hiring-departments", tags=["metrics"])
async def top_hiring_departments(session: SessionDep, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    """
    List of ids, names and number of employees hired for each department that hired more employees than the average in 2021.
    """
    try:
        # Use SQLModel with the view
        offset = (page - 1) * limit
        statement = select(VTopHiringDepartments).offset(offset).limit(limit)
        result = session.exec(statement)
        rows = result.all()

        # Convert to JSON format
        output = []
        for row in rows:
            output.append({
                "id": row.id,
                "department": row.department,
                "employees_hired": row.employees_hired
            })

        # Return response with pagination metadata
        return {
            "page": page,
            "limit": limit,
            "count": len(output),
            "data": output
        }

    except Exception as e:
        logger.error(f"Error in top_hiring_departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))
