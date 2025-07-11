# Fix Google Cloud Run Deployment Issues

Based on the error logs, here are the issues and solutions:

## 🔍 Issues Identified

1. **Worker Process Issues**: Gunicorn workers are failing to boot properly
2. **Memory Allocation**: Possible memory constraint issues
3. **File Dependencies**: Missing or incorrect package dependencies
4. **Configuration**: Cloud Run service configuration needs optimization

## 🛠️ Solutions

### 1. Fix Dockerfile Configuration
The Dockerfile has been optimized with:
- Proper requirements file handling
- Memory-efficient single worker with threads
- Non-root user security
- Health checks

### 2. Update Google Cloud Run Configuration
```bash
# Deploy with proper resource allocation
gcloud run deploy fit2hire \
    --image gcr.io/your-project-id/fit2hire \
    --region europe-west1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --concurrency 80 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --set-env-vars "FLASK_ENV=production,PORT=8080"
```

### 3. Environment Variables Required
Set these in Google Cloud Run:
```bash
DATABASE_URL=your-postgresql-connection-string
SESSION_SECRET=your-session-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FLASK_ENV=production
PORT=8080
```

### 4. Build and Deploy Commands
```bash
# Build the Docker image
docker build -t gcr.io/your-project-id/fit2hire .

# Push to Google Container Registry
docker push gcr.io/your-project-id/fit2hire

# Deploy to Cloud Run
gcloud run deploy fit2hire \
    --image gcr.io/your-project-id/fit2hire \
    --region europe-west1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --port 8080
```

### 5. Check Service Status
```bash
# Check service status
gcloud run services describe fit2hire --region europe-west1

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fit2hire" --limit=50
```

## 🚨 Common Cloud Run Issues

### Memory Issues
- **Symptom**: Worker processes failing to start
- **Solution**: Increase memory to 4GB minimum
- **Command**: `--memory 4Gi`

### Port Configuration
- **Symptom**: Service not responding to requests
- **Solution**: Ensure PORT environment variable is set
- **Command**: `--set-env-vars "PORT=8080"`

### Database Connection
- **Symptom**: Database connection errors
- **Solution**: Verify DATABASE_URL format
- **Format**: `postgresql://user:password@host:port/database`

### OAuth Configuration
- **Symptom**: Google Calendar authentication failing
- **Solution**: Update redirect URI in Google Cloud Console
- **URI**: `https://your-service-url/oauth2callback`

## 🔧 Troubleshooting Steps

1. **Check Logs**: Use Google Cloud Console Logs Explorer
2. **Verify Build**: Ensure Docker image builds without errors
3. **Test Locally**: Run container locally first
4. **Environment Variables**: Verify all required env vars are set
5. **Resource Limits**: Check memory and CPU allocation

## 📊 Monitoring

Set up monitoring to track:
- **Request latency**
- **Error rates**
- **Memory usage**
- **CPU utilization**
- **Instance scaling**

The deployment should now work properly with these fixes applied.