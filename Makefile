# Application configuration
APP_NAME = globant-data-engineering-challenge
APP_VERSION = 1.0
TAG = latest

# AWS ECR configuration (optional - for ECR deployment)
AWS_ECR_ACCOUNT_ID = 123456
AWS_ECR_REGION = us-east-1
AWS_ECR_REPO = $(APP_NAME)

# Port configuration
HOST_PORT = 8000
CONTAINER_PORT = 8000

.PHONY : help build run stop logs test clean docker/build docker/push docker/run docker/test

# Default command - show help
help:
	@echo "Available commands:"
	@echo "  make build     - Build Docker image"
	@echo "  make run       - Run application with docker-compose"
	@echo "  make stop      - Stop application"
	@echo "  make logs      - View application logs"
	@echo "  make test      - Test S3 endpoint"
	@echo "  make clean     - Clean containers and images"
	@echo "  make docker/build - Build Docker image manually"
	@echo "  make docker/push  - Push image to ECR (requires AWS configuration)"

# Build Docker image
build:
	docker-compose build

# Run application
run:
	docker-compose up -d

# Run application in development mode (with logs)
run-dev:
	docker-compose up

# Stop application
stop:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Test S3 endpoint
test:
	@echo "Testing S3 endpoint..."
	@curl -s "http://localhost:$(HOST_PORT)/test-s3?bucket_name=globant-data-engineering-challenge" | jq . || echo "Error: Make sure the application is running and jq is installed"

# Test root endpoint
test-root:
	@echo "Testing root endpoint..."
	@curl -s "http://localhost:$(HOST_PORT)/" | jq . || echo "Error: Make sure the application is running"

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
	aws ecr create-repository --repository-name $(AWS_ECR_REPO) || true
	docker tag $(APP_NAME):$(APP_VERSION) $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO):$(TAG)
	docker push $(AWS_ECR_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com/$(AWS_ECR_REPO):$(TAG)

# Run Docker image manually
docker/run:
	docker run -p $(HOST_PORT):$(CONTAINER_PORT) -v ~/.aws:/root/.aws:ro $(APP_NAME):$(APP_VERSION)

# Run tests (legacy - for compatibility)
docker/test:
	@echo "This command is for compatibility. Use 'make test' to test the FastAPI application"
