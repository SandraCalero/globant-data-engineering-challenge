# Application configuration
APP_NAME = globant-data-engineering-challenge
APP_VERSION = 1.0
TAG = latest

# AWS ECR configuration (optional - for ECR deployment)
AWS_ECR_ACCOUNT_ID = 362395301145
AWS_ECR_REGION = us-east-1
AWS_ECR_REPO = $(APP_NAME)

# Port configuration
HOST_PORT = 8000
CONTAINER_PORT = 8000

.PHONY : help build run run-local stop logs test test-batch clean docker/build docker/push docker/run docker/test

# Default command - show help
help:
	@echo "Available commands:"
	@echo "  make build       - Build Docker image"
	@echo "  make run         - Run application with docker-compose (development)"
	@echo "  make run-local   - Run application locally (without Docker)"
	@echo "  make stop        - Stop application"
	@echo "  make logs        - View application logs"
	@echo "  make test-db     - Test db endpoint"
	@echo "  make test-s3     - Test S3 endpoint"
	@echo "  make test-batch  - Test all batch endpoints"
	@echo "  make test-dept   - Test departments batch endpoint"
	@echo "  make test-emp    - Test employees batch endpoint"
	@echo "  make test-jobs   - Test jobs batch endpoint"
	@echo "  make test-metrics - Test metrics endpoints"
	@echo "  make clean       - Clean containers and images"
	@echo "  make docker/build - Build Docker image manually"
	@echo "  make docker/push  - Push image to ECR (requires AWS configuration)"

# Build Docker image
build:
	docker-compose build

# Run application (development)
run:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# Run application in development mode (with logs)
run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml up

# Run application locally (without Docker)
run-local:
	@echo "Starting application locally..."
	@python -m uvicorn app.main:app --host 0.0.0.0 --port $(HOST_PORT) --reload

# Stop application
stop:
	docker-compose -f docker-compose.yml -f docker-compose.local.yml down

# View logs
logs:
	docker-compose logs -f

# Test db endpoint
test-db:
	@echo "Testing db endpoint..."
	@curl -s "http://localhost:$(HOST_PORT)/health-db" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test S3 endpoint
test-s3:
	@echo "Testing S3 endpoint..."
	@curl -s "http://localhost:$(HOST_PORT)/health-s3" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test root endpoint
test-root:
	@echo "Testing root endpoint..."
	@curl -s "http://localhost:$(HOST_PORT)/" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test all batch endpoints
test-batch: test-dept test-emp test-jobs
	@echo "All batch endpoints tested!"

# Test all tables batch endpoint
test-all-tables:
	@echo "Testing all tables batch endpoint..."
	@curl -s -X POST "http://localhost:$(HOST_PORT)/all-tables/batch" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test departments batch endpoint
test-dept:
	@echo "Testing departments batch endpoint..."
	@curl -s -X POST "http://localhost:$(HOST_PORT)/departments/batch" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test employees batch endpoint
test-emp:
	@echo "Testing employees batch endpoint..."
	@curl -s -X POST "http://localhost:$(HOST_PORT)/employees/batch" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test jobs batch endpoint
test-jobs:
	@echo "Testing jobs batch endpoint..."
	@curl -s -X POST "http://localhost:$(HOST_PORT)/jobs/batch" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test GET endpoints
test-get:
	@echo "Testing GET endpoints..."
	@echo "Departments:"
	@curl -s "http://localhost:$(HOST_PORT)/departments" | jq . || echo "Error"
	@echo "Employees:"
	@curl -s "http://localhost:$(HOST_PORT)/employees" | jq . || echo "Error"
	@echo "Jobs:"
	@curl -s "http://localhost:$(HOST_PORT)/jobs" | jq . || echo "Error"

# Test metrics endpoints
test-metrics:
	@echo "Testing metrics endpoints..."
	@echo "Hired by Quarter 2021:"
	@curl -s "http://localhost:$(HOST_PORT)/metrics/hired-by-quarter-2021?page=1&limit=3" | jq . || echo "Error"
	@echo "Top Hiring Departments:"
	@curl -s "http://localhost:$(HOST_PORT)/metrics/top-hiring-departments?page=1&limit=3" | jq . || echo "Error"

# Clean containers and images
clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -f

# Build Docker image manually
docker/build:
	docker build -t $(APP_NAME):$(APP_VERSION) .

# Push to ECR (requires AWS configuration)
docker/push: docker/build
	aws ecr get-login-password --region $(AWS_ECR_REGION) | docker login --username AWS --password-stdin $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com
	docker tag $(APP_NAME):$(APP_VERSION) $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO):$(TAG)
	docker push $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO):$(TAG)

# Run Docker image manually
docker/run:
	docker run -p $(HOST_PORT):$(CONTAINER_PORT) -v ~/.aws:/root/.aws:ro $(APP_NAME):$(APP_VERSION)

# Run tests (legacy - for compatibility)
docker/test:
	@echo "This command is for compatibility. Use 'make test' to test the FastAPI application"
