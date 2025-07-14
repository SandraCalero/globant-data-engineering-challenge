# Installation Guide

## Prerequisites

- Docker and Docker Compose
- AWS CLI configured with credentials (for local dev)
- Python 3.12+ (for local development)
- jq (optional, for JSON formatting in tests)

## Local Development Setup

### 1. Clone and setup
```bash
git clone <repository-url>
cd globant-data-engineering-challenge
aws configure  # Configure AWS credentials
```

### 2. Create environment file
```bash
cp env.example .env
# Edit .env with your configuration:
# ENV=current_env
# S3_BUCKET_NAME=your-s3-bucket-name
# DB_HOST=db
# DATABASE_URL=postgresql+psycopg2://myuser:mypassword@db:5432/mydatabase
# POSTGRES_USER=myuser
# POSTGRES_PASSWORD=mypassword
# POSTGRES_DB=mydatabase
# LOG_LEVEL=INFO
```

### 3. Run the application
```bash
make run
```

### 4. Verify the setup
```bash
# Check if containers are running
docker ps

# Check application logs
make logs

# Test health endpoints
curl http://localhost:8000/
curl http://localhost:8000/health-db
curl http://localhost:8000/health-s3
```

## Docker Commands (Alternative to Makefile)

If you prefer using Docker commands directly:

```bash
# Build and run the application
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build

# Run in background
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# Stop the application
docker-compose -f docker-compose.yml -f docker-compose.local.yml down

# View logs
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f

# Execute commands inside the container
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi bash

# Run Alembic commands
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi alembic upgrade head
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi alembic revision --autogenerate -m "migration_name"
```

## Environment Variables

### Local Development
```bash
export ENV=current_env
export S3_BUCKET_NAME=your-s3-bucket-name
export DB_HOST=db
export DATABASE_URL=postgresql+psycopg2://user:password@db:5432/database
export POSTGRES_USER=myuser
export POSTGRES_PASSWORD=mypassword
export POSTGRES_DB=mydatabase
export LOG_LEVEL=INFO
```

### Production (ECS/Fargate)
- Access to S3 and other services is managed through the **IAM Task Role**
- Database credentials (`DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`) are managed through **AWS Secrets Manager**

## Makefile Commands

```bash
make help            # View all commands
make build           # Build Docker image
make run             # Run application with docker-compose (development)
make run-dev         # Run application in development mode (with logs)
make run-local       # Run application locally (without Docker)
make stop            # Stop application
make logs            # View application logs
make test-db         # Test db endpoint
make test-s3         # Test S3 endpoint
make test-root       # Test root endpoint
make test-batch      # Test all batch endpoints
make test-all-tables # Test all tables batch endpoint
make test-dept       # Test departments batch endpoint
make test-emp        # Test employees batch endpoint
make test-jobs       # Test jobs batch endpoint
make test-get        # Test GET endpoints
make test-metrics    # Test metrics endpoints
make clean           # Clean containers and images
make docker/build    # Build Docker image manually
make docker/push     # Push image to ECR (requires AWS configuration)
make docker/run      # Run Docker image manually
make docker/test     # Legacy test command
``` 