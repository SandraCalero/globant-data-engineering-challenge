# Globant Data Engineering Challenge

## 📋 Description

FastAPI application to process employee data from CSV files stored in S3 and store them in a database. The application is designed to be deployed on AWS ECS with Fargate, using cloud-native security and deployment best practices.

## 🏗️ Architecture
```text
┌────────────────────────────────────────────────────┐
│                    End User                        │
│              (consumes API endpoints)              │
└────────────────────────────────────────────────────┘
                 │                 ▲
                 ▼                 │
┌────────────────────────────────────────────────────┐
│         Application Load Balancer (ALB)            │
│         (exposes public API endpoints)             │
└────────────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│             ECS Cluster (Fargate)                  │
│     (runs FastAPI container)                       │
│      - Task Definition (Docker image)              │
│      - Auto scaling                                │
└────────────────────────────────────────────────────┘
      │                      │
      ▼                      ▼
┌────────────────┐    ┌────────────────────────────┐
│   S3 Bucket    │    │      Aurora Database       │
│  (CSV files)   │    │  (stores loaded data)      │
└────────────────┘    └────────────────────────────┘
```

## 🚀 Features

### ✅ Implemented
- **FastAPI Application**: REST API with endpoints for departments, jobs and employees
- **Batch Processing**: Endpoints to process CSV files in batches (1-1000 rows)
- **Data Models**: SQLModel for departments, jobs and employees with proper relationships
- **S3 Connection**: Service class to read files from S3 buckets
- **Database Connection**: Aurora PostgreSQL with health check
- **Docker**: Container with FastAPI and hot-reload for development
- **Docker Compose**: Configuration for local development with PostgreSQL
- **Makefile**: Simplified commands for development and deployment
- **Security**: Uses IAM Task Role for S3 access and AWS Secrets Manager for database URL

### 🔧 Available Endpoints

#### Health & Status
- `GET /` - Root endpoint
- `GET /health-db` - Health check for database connection
- `GET /health-s3` - Health check for S3 connection and file listing

#### Data Processing
- `POST /departments/batch` - Process departments from CSV file (departments.csv)
- `POST /jobs/batch` - Process jobs from CSV file (jobs.csv)
- `POST /employees/batch` - Process employees from CSV file (hired_employees.csv)

#### Data Retrieval
- `GET /departments` - List all departments
- `GET /jobs` - List all jobs
- `GET /employees` - List all employees

## 🛠️ Technologies Used

- **FastAPI**: Web framework for APIs
- **SQLModel**: Modern ORM for Python
- **boto3**: AWS SDK for Python
- **Docker**: Containers
- **PostgreSQL**: Local development database
- **AWS S3**: File storage
- **AWS ECR**: Container registry
- **AWS ECS/Fargate**: Serverless container orchestration

## 🚀 Installation and Usage

### Prerequisites
- Docker and Docker Compose
- AWS CLI configured with credentials (for local dev)
- Python 3.12+ (for local development)
- jq (optional, for JSON formatting in tests)

### Local Development

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd globant-data-engineering-challenge
   aws configure  # Configure AWS credentials
   ```

2. **Run the application**
   ```bash
   make run
   ```

### Makefile Commands

```bash
make help         # View all commands
make build        # Build Docker image
make run          # Run application (development)
make run-dev      # Run with visible logs
make run-local    # Run locally without Docker
make stop         # Stop application
make logs         # View logs
make test-s3      # Test S3 endpoint
make test-db      # Test database endpoint
make test-batch   # Test all batch endpoints
make test-dept    # Test departments batch endpoint
make test-emp     # Test employees batch endpoint
make test-jobs    # Test jobs batch endpoint
make test-get     # Test GET endpoints
make clean        # Clean containers
```

### Environment Variables

#### Local Development
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
export S3_BUCKET_NAME=your-bucket-name
```

#### Production (ECS/Fargate)
- Access to S3 and other services is managed through the **IAM Task Role**
- `DATABASE_URL` is securely injected from **AWS Secrets Manager**

## 🔍 Testing

### Test batch endpoints
```bash
# Process departments
curl -X POST "http://localhost:8000/departments/batch"

# Process employees
curl -X POST "http://localhost:8000/employees/batch"

# Process jobs
curl -X POST "http://localhost:8000/jobs/batch"
```

### Test GET endpoints
```bash
curl "http://localhost:8000/departments"
curl "http://localhost:8000/employees"
curl "http://localhost:8000/jobs"
```

## 📊 Batch Processing Features

- **Batch Size Control**: Configurable batch size (default: 1000 rows)
- **Transaction Support**: Commits per batch, not per row
- **Error Handling**: Robust error handling with detailed logging
- **Upsert Logic**: Insert new records or update existing ones
- **Data Validation**: Automatic validation using SQLModel
- **Performance Optimizations**: Efficient queries and memory management

## 📝 Next Steps

- [ ] Add unit tests
- [ ] Configure CI/CD pipeline
- [ ] Add data validation rules

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.
