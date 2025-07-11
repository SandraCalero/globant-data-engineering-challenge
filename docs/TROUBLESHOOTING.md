# Troubleshooting Guide

## Common Issues

### Database connection fails
```bash
# Check if database container is running
docker ps | grep postgres

# Check database logs
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs db

# Verify environment variables
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi env | grep POSTGRES
```

### Migrations not applied
```bash
# Check migration status
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi alembic current

# Apply migrations manually
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi alembic upgrade head

# Check migration history
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi alembic history
```

### S3 connection issues
```bash
# Test S3 connectivity
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi python -c "import boto3; s3 = boto3.client('s3'); print(s3.list_buckets())"

# Verify AWS credentials
docker-compose -f docker-compose.yml -f docker-compose.local.yml exec fastapi env | grep AWS
```

### Container startup issues
```bash
# Rebuild containers
docker-compose -f docker-compose.yml -f docker-compose.local.yml down
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build

# Check container logs
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs fastapi
```

### Permission issues
```bash
# Fix file permissions
chmod +x entrypoint.sh

# Fix Docker permissions
sudo chown $USER:$USER ~/.docker -R
```

### Port conflicts
```bash
# Check if port 8000 is in use
lsof -i :8000

# Check if port 5432 is in use
lsof -i :5432

# Use different ports in docker-compose.local.yml
```

## Error Messages and Solutions

### "Database is uninitialized and superuser password is not specified"
- **Cause**: Missing or empty `POSTGRES_PASSWORD` environment variable
- **Solution**: Ensure `.env` file has `POSTGRES_PASSWORD=mypassword`

### "Could not parse SQLAlchemy URL"
- **Cause**: Missing or malformed `DATABASE_URL`
- **Solution**: Check `.env` file and ensure `DATABASE_URL` is properly formatted

### "ImportError: attempted relative import with no known parent package"
- **Cause**: Alembic trying to import models with relative imports
- **Solution**: Use absolute imports in `alembic/env.py`

### "NameError: name 'sqlmodel' is not defined"
- **Cause**: Missing `import sqlmodel` in migration files
- **Solution**: Add `import sqlmodel` to the top of migration files

### "pg_isready: command not found"
- **Cause**: PostgreSQL client not installed in container
- **Solution**: Ensure Dockerfile includes `postgresql-client` installation

## Performance Issues

### Slow database queries
- Check if indexes are created properly
- Verify database connection pooling
- Monitor query execution plans

### Memory issues
- Increase Docker memory limits
- Check for memory leaks in application
- Monitor container resource usage

## Network Issues

### Container can't reach database
- Verify network configuration in docker-compose
- Check if database host is correct
- Ensure firewall rules allow connections

### S3 connectivity issues
- Verify AWS credentials are configured
- Check IAM permissions for S3 access
- Ensure network allows outbound HTTPS connections 