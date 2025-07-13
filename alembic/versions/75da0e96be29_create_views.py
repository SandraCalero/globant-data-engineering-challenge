"""create_views

Revision ID: 75da0e96be29
Revises: d10963c20708
Create Date: 2025-07-12 22:17:22.924687

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import text
from sqlalchemy_views import CreateView, DropView


# revision identifiers, used by Alembic.
revision: str = '75da0e96be29'
down_revision: Union[str, Sequence[str], None] = 'd10963c20708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HIRED_BY_QUARTER_VIEW = Table('vhiredbyquarter2021', MetaData())
TOP_HIRING_VIEW = Table('vtophiringdepartments', MetaData())


def upgrade() -> None:
    """Upgrade schema."""

    # Create view for hired by quarter 2021
    create_hired_by_quarter_view = CreateView(
        HIRED_BY_QUARTER_VIEW,
        text("""
        WITH hires_2021 AS (
            SELECT 
                e.department_id,
                e.job_id,
                EXTRACT(QUARTER FROM e.hire_date) AS quarter
            FROM employee e
            WHERE EXTRACT(YEAR FROM e.hire_date) = 2021
        )
        SELECT 
            d.department,
            j.job,
            COUNT(CASE WHEN h.quarter = 1 THEN 1 END) AS Q1,
            COUNT(CASE WHEN h.quarter = 2 THEN 1 END) AS Q2,
            COUNT(CASE WHEN h.quarter = 3 THEN 1 END) AS Q3,
            COUNT(CASE WHEN h.quarter = 4 THEN 1 END) AS Q4
        FROM hires_2021 h
        JOIN department d ON h.department_id = d.id
        JOIN job j ON h.job_id = j.id
        GROUP BY d.department, j.job
        ORDER BY d.department, j.job
        """),
        or_replace=True
    )
    op.execute(create_hired_by_quarter_view)

    # Create view for top hiring departments
    create_top_hiring_view = CreateView(
        TOP_HIRING_VIEW,
        text("""
        WITH dept_hires_2021 AS (
            SELECT 
                d.id,
                d.department,
                COUNT(e.id) as employees_hired
            FROM department d
            LEFT JOIN employee e ON d.id = e.department_id 
                AND EXTRACT(YEAR FROM e.hire_date) = 2021
            GROUP BY d.id, d.department
        )
        SELECT 
            id,
            department,
            employees_hired
        FROM dept_hires_2021
        WHERE employees_hired > (SELECT AVG(employees_hired) FROM dept_hires_2021)
        ORDER BY employees_hired DESC
        """),
        or_replace=True
    )
    op.execute(create_top_hiring_view)


def downgrade() -> None:
    """Downgrade schema."""
    drop_hired_view = DropView(HIRED_BY_QUARTER_VIEW, if_exists=True)
    drop_top_view = DropView(TOP_HIRING_VIEW, if_exists=True)
    op.execute(drop_hired_view)
    op.execute(drop_top_view)
