# Docker Deployment Guide for Resume Match AI

## Quick Start with Docker

### Option 1: Using Docker Compose (Recommended for beginners)

```bash
# 1. Clone or download your project files
# 2. Create environment file
cp .env.example .env

# 3. Edit .env file with your settings
# 4. Start the application with database
docker-compose up -d

# 5. Access your application
# Open http://localhost:5000 in your browser
```

### Option 2: Build and Run Docker Container

```bash
# Build the Docker image
docker build -t resume-match-ai .

# Run with external database
docker run -d \
  --name resume-app \
  -p 5000:5000 \
  -e DATABASE_URL="your-database-connection-string" \
  -e SESSION_SECRET="your-secret-key" \
  resume-match-ai

# Access your application
# Open http://localhost:5000 in your browser
```

## Deployment Options

### 1. Google Cloud Run (Serverless)
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/resume-match-ai

# Deploy to Cloud Run
gcloud run deploy resume-match-ai \
  --image gcr.io/YOUR_PROJECT_ID/resume-match-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="your-connection-string",SESSION_SECRET="your-secret"
```

### 2. AWS ECS (Amazon)
```bash
# Tag and push to AWS ECR
docker tag resume-match-ai:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/resume-match-ai:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/resume-match-ai:latest

# Deploy using ECS task definition
```

### 3. Digital Ocean App Platform
```bash
# Push to Docker Hub
docker tag resume-match-ai YOUR_USERNAME/resume-match-ai
docker push YOUR_USERNAME/resume-match-ai

# Deploy via Digital Ocean console using the image
```

### 4. Local Development
```bash
# For development with auto-reload
docker-compose -f docker-compose.dev.yml up
```

## Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session security

Optional:
- `FLASK_ENV`: Set to 'development' for debugging
- `FLASK_DEBUG`: Set to 'True' for debug mode

## Production Considerations

### Security
- Change default passwords in docker-compose.yml
- Use strong SESSION_SECRET
- Enable HTTPS in production
- Set FLASK_ENV=production

### Performance
- Use multiple workers: `--workers 4`
- Set appropriate memory limits
- Enable connection pooling for database

### Monitoring
```bash
# View logs
docker logs resume-app

# Monitor container stats
docker stats resume-app
```

## Troubleshooting

### Common Issues:
1. **Port already in use**: Change port mapping `-p 5001:5000`
2. **Database connection**: Check DATABASE_URL format
3. **Memory issues**: Increase Docker memory allocation
4. **Permission errors**: Check file permissions for uploads folder

### Debug Commands:
```bash
# Access container shell
docker exec -it resume-app bash

# Check environment variables
docker exec resume-app env

# View application logs
docker logs -f resume-app
```

## Cost Estimation

### Cloud Run (Google): $0-10/month for low traffic
### ECS (AWS): $15-30/month with t3.micro
### Digital Ocean: $5-20/month
### Self-hosted: $5-50/month depending on server

## Scaling

For high traffic:
```yaml
# docker-compose.yml
web:
  deploy:
    replicas: 3
  
nginx:
  image: nginx
  # Add load balancer configuration
```