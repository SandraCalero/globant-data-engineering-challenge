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

## 🚀 Current Project Status

### ✅ Implemented

- **FastAPI Application**: REST API with endpoints for departments, jobs and employees
- **Data Models**: SQLModel for departments, jobs and employees
- **S3 Connection**: Service class to read files from S3 buckets
- **Database Connection**: Aurora PostgreSQL with health check
- **Health Checks**: Endpoints for S3 and database connectivity
- **Docker**: Container with FastAPI and hot-reload
- **Docker Compose**: Configuration for local development
- **Makefile**: Simplified commands for development and deployment
- **Logging**: Detailed logging system for debugging
- **Error Handling**: Robust error handling for AWS and S3
- **Security**: Uses IAM Task Role for S3 access and AWS Secrets Manager for database URL in production

### 🔧 Available Endpoints

- `GET /` - Root endpoint
- `GET /health-db` - Health check for database connection
- `GET /health-s3` - Health check for S3 connection and file listing
- `POST /departments` - Create department
- `GET /departments` - List departments
- `POST /jobs` - Create job
- `POST /employees` - Create employee

### 📁 Project Structure

```
globant-data-engineering-challenge/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLModel models
│   ├── db.py            # Database configuration
│   ├── services.py      # Reusable service classes (S3, DB)
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker image definition
├── Makefile             # Development commands
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🛠️ Technologies Used

- **FastAPI**: Web framework for APIs
- **SQLModel**: Modern ORM for Python
- **boto3**: AWS SDK for Python
- **Docker**: Containers
- **Docker Compose**: Container orchestration
- **AWS S3**: File storage
- **AWS ECR**: Container registry
- **AWS ECS/Fargate**: Serverless container orchestration
- **AWS Secrets Manager**: Secure storage for secrets (e.g., DATABASE_URL)
- **IAM Task Role**: Secure access to AWS resources from ECS

## 🚀 Installation and Usage

### Prerequisites

- Docker and Docker Compose
- AWS CLI configured with credentials (for local dev)
- Python 3.12+ (for local development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd globant-data-engineering-challenge
   ```

2. **Configure AWS credentials (for local dev only)**
   ```bash
   aws configure
   ```

3. **Run the application**
   ```bash
   make run
   ```

4. **Test endpoints**
   ```bash
   make test
   make test-root
   ```

### Makefile Commands

```bash
make help      # View all commands
make build     # Build Docker image
make run       # Run application
make run-dev   # Run with visible logs
make stop      # Stop application
make logs      # View logs
make test      # Test S3 endpoint
make clean     # Clean containers
```

### Environment Variables

#### Local Development

The application uses AWS CLI credentials automatically for local development. If you need to use environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Production (ECS/Fargate)
- **You do not need to define AWS keys in environment variables.**
- Access to S3 and other services is managed through the **IAM Task Role** associated with the task.
- The variable `DATABASE_URL` is securely injected from **AWS Secrets Manager** using the `ValueFrom` option in the Task Definition.


## 🔍 Testing

> **Note:** To test the database health check endpoint locally, you need to have a local database running. The Aurora database in AWS (Serverless v2) cannot be accessed from your local environment because it does not expose a public endpoint.

### Test S3 health check
```bash
curl "http://localhost:8000/health-s3"
```

### Test database health check
```bash
curl "http://localhost:8000/health-db"
```

### Test root endpoint
```bash
curl "http://localhost:8000/"
```

## 📝 Next Steps

- [ ] Implement CSV file processing
- [ ] Add unit tests
- [ ] Configure CI/CD pipeline
- [ ] Deploy to AWS ECS (production ready)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

