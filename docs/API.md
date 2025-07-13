# API Documentation

## Base URL
```
http://localhost:8000
```

## Available Endpoints

### Health & Status
- `GET /` - Root endpoint
- `GET /health-db` - Health check for database connection
- `GET /health-s3` - Health check for S3 connection and file listing

### Data Processing
- `POST /departments/batch` - Process departments from CSV file (departments.csv)
- `POST /jobs/batch` - Process jobs from CSV file (jobs.csv)
- `POST /employees/batch` - Process employees from CSV file (hired_employees.csv)
- `POST /all-tables/batch` - Process all CSV files simultaneously

### Data Retrieval
- `GET /departments` - List all departments (with pagination)
- `GET /jobs` - List all jobs (with pagination)
- `GET /employees` - List all employees (with pagination)

### Analytics & Metrics
- `GET /metrics/hired-by-quarter-2021` - Number of employees hired for each position and department in 2021 divided by quarter
- `GET /metrics/top-hiring-departments` - List of departments that hired more employees than the average in 2021

## Testing Examples

### Test batch endpoints
```bash
# Process departments
curl -X POST "http://localhost:8000/departments/batch"

# Process employees
curl -X POST "http://localhost:8000/employees/batch"

# Process jobs
curl -X POST "http://localhost:8000/jobs/batch"

# Process all tables at once
curl -X POST "http://localhost:8000/all-tables/batch"
```

### Test GET endpoints (with pagination)
```bash
# Get departments with pagination (default: page=1, limit=10)
curl "http://localhost:8000/departments?page=1&limit=20"

# Get employees with pagination
curl "http://localhost:8000/employees?page=1&limit=50"

# Get jobs with pagination
curl "http://localhost:8000/jobs?page=1&limit=100"

# Test metrics endpoints
curl "http://localhost:8000/metrics/hired-by-quarter-2021?page=1&limit=5"
curl "http://localhost:8000/metrics/top-hiring-departments?page=1&limit=10"

### Test health endpoints
```bash
# Root endpoint
curl "http://localhost:8000/"

# Database health check
curl "http://localhost:8000/health-db"

# S3 health check
curl "http://localhost:8000/health-s3"
```

## Response Formats

### Department Response
```json
{
  "id": 1,
  "department": "Engineering"
}
```

### Job Response
```json
{
  "id": 1,
  "job": "Software Engineer"
}
```

### Employee Response
```json
{
  "id": 1,
  "name": "John Doe",
  "hire_date": "2023-01-15T00:00:00",
  "department_id": 1,
  "job_id": 1
}
```

### Hired by Quarter 2021 Response
```json
{
  "page": 1,
  "limit": 5,
  "count": 5,
  "data": [
    {
      "department": "Accounting",
      "job": "Account Representative IV",
      "Q1": 1,
      "Q2": 0,
      "Q3": 0,
      "Q4": 0
    }
  ]
}
```

### Top Hiring Departments Response
```json
{
  "page": 1,
  "limit": 10,
  "count": 7,
  "data": [
    {
      "id": 8,
      "department": "Support",
      "employees_hired": 217
    }
  ]
}
```

### Batch Processing Response
```json
{
  "table": "departments",
  "total": 1000,
  "inserted": 950,
  "updated": 50,
  "failed": 0,
  "errors": [],
  "file_not_found": false
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "database_connected": true
}
```

### S3 Health Check Response
```json
{
  "status": "healthy",
  "s3_connected": true,
  "files_count": 3,
  "files": [
    {"key": "Departments/departments.csv"},
    {"key": "Jobs/jobs.csv"},
    {"key": "Employees/hired_employees.csv"}
  ],
  "error": null
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Query Parameters

### Pagination
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 10, max: 100)

## Batch Processing Features

- **Batch Size Control**: Configurable batch size (default: 1000 rows)
- **Transaction Support**: Commits per batch, not per row
- **Error Handling**: Robust error handling with detailed logging
- **Upsert Logic**: Insert new records or update existing ones
- **Data Validation**: Automatic validation using SQLModel
- **Performance Optimizations**: Efficient queries and memory management
- **Scalable S3 Structure**: CSV files organized in folders by model class (Departments/, Jobs/, Employees/)
- **Batch All Tables**: Process all CSV files simultaneously with single endpoint
- **Pagination Support**: GET endpoints support pagination for better performance

## Analytics & Metrics Features

- **Database Views**: Optimized SQL views for complex analytics queries
- **SQLModel Integration**: Type-safe models for database views
- **Pagination Support**: All metrics endpoints support pagination
- **Consistent Response Format**: Standardized pagination metadata across all endpoints 