# Complete Google Cloud Platform Deployment Guide for Fit2Hire

This guide provides everything you need to deploy Fit2Hire to Google Cloud Run with full Google Calendar integration.

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed locally
3. **Docker** installed locally
4. **Project ID** in Google Cloud Console

## 🚀 Quick Deployment

### Option 1: Using the Deploy Script (Recommended)

```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Run the deployment script
./deploy.sh
```

### Option 2: Manual Deployment

```bash
# 1. Build the Docker image
docker build -t gcr.io/your-project-id/fit2hire .

# 2. Push to Container Registry
docker push gcr.io/your-project-id/fit2hire

# 3. Deploy to Cloud Run
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
    --port 8080
```

## 🔧 Configuration Details

### Dockerfile Features
- **Multi-stage build** for smaller image size
- **Non-root user** for security
- **Health checks** for reliability
- **Optimized Gunicorn** settings for Cloud Run
- **spaCy model** pre-downloaded
- **4GB memory** allocation for NLP processing

### Cloud Run Configuration
- **Memory**: 4GB (required for spaCy + ML libraries)
- **CPU**: 2 cores (optimal for performance)
- **Timeout**: 3600 seconds (1 hour for long operations)
- **Concurrency**: 80 requests per instance
- **Auto-scaling**: 1-10 instances based on traffic

## 🗄️ Database Setup

### Using Cloud SQL (Recommended)
```bash
# Create Cloud SQL instance
gcloud sql instances create fit2hire-db \
    --database-version=POSTGRES_13 \
    --cpu=2 \
    --memory=4GB \
    --region=europe-west1 \
    --storage-size=20GB

# Create database
gcloud sql databases create fit2hire --instance=fit2hire-db

# Create user
gcloud sql users create fit2hire-user \
    --instance=fit2hire-db \
    --password=your-secure-password
```

### Environment Variables
Set these in Cloud Run:
```bash
DATABASE_URL=postgresql://fit2hire-user:password@/fit2hire?host=/cloudsql/project:region:instance
SESSION_SECRET=your-session-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 📅 Google Calendar Integration Setup

### 1. Google Cloud Console Configuration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Configure OAuth consent screen:
   - User Type: External
   - App name: Fit2Hire
   - Scopes: `https://www.googleapis.com/auth/calendar`
   - Test users: Add your email

### 2. Create OAuth Credentials
1. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
2. Application type: Web application
3. Name: Fit2Hire Calendar Integration
4. Authorized redirect URIs: `https://your-service-url/oauth2callback`

### 3. Update Environment Variables
```bash
# Set environment variables in Cloud Run
gcloud run services update fit2hire \
    --region europe-west1 \
    --set-env-vars "GOOGLE_CLIENT_ID=your-client-id,GOOGLE_CLIENT_SECRET=your-client-secret"
```

## 🛠️ Advanced Configuration

### Custom Domain Setup
```bash
# Map custom domain
gcloud run domain-mappings create \
    --service fit2hire \
    --domain your-domain.com \
    --region europe-west1
```

### SSL Certificate
```bash
# Cloud Run automatically provides SSL certificates for custom domains
# Update your DNS records to point to the Cloud Run service
```

### Monitoring and Logging
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fit2hire"
```

## 🔒 Security Best Practices

1. **Environment Variables**: Store secrets in Cloud Run environment variables
2. **IAM Roles**: Use least privilege principle
3. **VPC Connector**: For private database access
4. **Cloud Armor**: For DDoS protection
5. **Identity-Aware Proxy**: For additional authentication

## 📊 Performance Optimization

### Memory Settings
- **4GB RAM**: Required for spaCy model and ML processing
- **Single worker**: With multiple threads (better for I/O-bound tasks)
- **Request limits**: 1000 requests per worker before restart

### Scaling Configuration
- **Min instances**: 1 (always warm)
- **Max instances**: 10 (cost control)
- **Concurrency**: 80 (optimal for mixed workloads)

## 🐛 Troubleshooting

### Common Issues
1. **Memory errors**: Increase memory allocation to 4GB
2. **Cold starts**: Set min-instances to 1
3. **OAuth errors**: Check redirect URI configuration
4. **Database connection**: Verify Cloud SQL proxy setup

### Monitoring
```bash
# Check service status
gcloud run services describe fit2hire --region europe-west1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Monitor metrics
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"
```

## 💰 Cost Optimization

### Resource Allocation
- **CPU**: 2 cores (balanced performance/cost)
- **Memory**: 4GB (minimum for NLP processing)
- **Min instances**: 1 (reduces cold starts)
- **Request timeout**: 3600s (for long-running operations)

### Estimated Monthly Costs
- **Cloud Run**: ~$50-200/month (depends on traffic)
- **Cloud SQL**: ~$60-150/month (depends on instance size)
- **Storage**: ~$5-20/month (depends on data volume)

## 🔄 CI/CD Pipeline

### Cloud Build Integration
The `cloudbuild.yaml` file automates:
1. Docker image building
2. Container Registry push
3. Cloud Run deployment
4. Environment variable setup

### GitHub Actions (Optional)
```yaml
name: Deploy to Cloud Run
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    - run: gcloud builds submit --config cloudbuild.yaml
```

## 📝 Post-Deployment Checklist

- [ ] Service is accessible via HTTPS
- [ ] Database connection is working
- [ ] File uploads are functioning
- [ ] Google Calendar OAuth is configured
- [ ] Environment variables are set
- [ ] SSL certificate is active
- [ ] Monitoring is enabled
- [ ] Backup strategy is in place

## 🆘 Support

For deployment issues:
1. Check Cloud Run logs
2. Verify environment variables
3. Test database connectivity
4. Validate OAuth configuration
5. Monitor resource usage

Your Fit2Hire application is now production-ready on Google Cloud Run!