# Complete Google Cloud Platform Deployment Guide

## 🚀 Quick Deployment (Recommended)

### Option 1: Automated Script Deployment
```bash
# Make script executable and run
chmod +x deploy.sh
./deploy.sh

# Choose option 1 for App Engine or 2 for Cloud Run
```

### Option 2: Manual Step-by-Step

## 📋 Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **Project created** in Google Cloud Console

## 🛠️ Setup Commands

### 1. Initial Setup
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 2. Create Database
```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create resume-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=10GB

# Create database
gcloud sql databases create resumematchai --instance=resume-db

# Create user (replace with strong password)
gcloud sql users create appuser \
    --instance=resume-db \
    --password=YOUR_STRONG_PASSWORD

# Get connection string (save this!)
gcloud sql instances describe resume-db --format="value(connectionName)"
```

## 🚀 Deployment Options

### Option A: App Engine Deployment

1. **Create environment file**:
```bash
cp .env.yaml.template .env.yaml
# Edit .env.yaml with your database credentials
```

2. **Initialize App Engine**:
```bash
gcloud app create --region=us-central1
```

3. **Deploy**:
```bash
gcloud app deploy app.yaml --env-vars-file=.env.yaml
```

4. **Open application**:
```bash
gcloud app browse
```

### Option B: Cloud Run Deployment

1. **Build Docker image**:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/resume-match-ai
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy resume-match-ai \
    --image gcr.io/YOUR_PROJECT_ID/resume-match-ai \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --set-env-vars DATABASE_URL="your-db-connection-string" \
    --set-env-vars SESSION_SECRET="your-secret-key" \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:resume-db
```

3. **Get service URL**:
```bash
gcloud run services describe resume-match-ai --region us-central1 --format="value(status.url)"
```

## 📁 File Overview

Created deployment files:
- **app.yaml** - App Engine configuration
- **cloudbuild.yaml** - Cloud Build configuration  
- **cloud-run.yaml** - Cloud Run service definition
- **requirements-appengine.txt** - Python dependencies
- **deploy.sh** - Automated deployment script
- **.env.yaml.template** - Environment variables template
- **Dockerfile** - Container configuration
- **.gcloudignore** - Files to ignore during deployment

## 💰 Cost Estimation

### App Engine:
- **Database (F1-micro)**: ~$7-10/month
- **App Engine (F2 instance)**: ~$10-20/month for low traffic
- **Total**: ~$17-30/month

### Cloud Run:
- **Database (F1-micro)**: ~$7-10/month  
- **Cloud Run**: Pay-per-use, ~$0-15/month for low traffic
- **Total**: ~$7-25/month

## 🔧 Configuration Details

### Database Connection Format:
```
postgresql://username:password@/database?host=/cloudsql/PROJECT_ID:REGION:INSTANCE
```

### Environment Variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Random secret key for sessions
- `FLASK_ENV`: Set to "production"

## 🚨 Security Checklist

- [ ] Strong database password (12+ characters)
- [ ] Random session secret key (32+ characters)
- [ ] Firewall rules configured
- [ ] SSL/HTTPS enabled (automatic)
- [ ] Environment variables secured

## 📊 Monitoring & Logs

### View Application Logs:
```bash
# App Engine
gcloud app logs tail

# Cloud Run  
gcloud run services logs read resume-match-ai --region us-central1
```

### Monitor Performance:
- Google Cloud Console: https://console.cloud.google.com
- App Engine: https://console.cloud.google.com/appengine
- Cloud Run: https://console.cloud.google.com/run

## 🔄 Updates & Maintenance

### Update Application:
```bash
# App Engine
gcloud app deploy app.yaml --env-vars-file=.env.yaml

# Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/resume-match-ai
gcloud run deploy resume-match-ai --image gcr.io/YOUR_PROJECT_ID/resume-match-ai --region us-central1
```

### Database Backup:
```bash
# Create backup
gcloud sql backups create --instance=resume-db

# List backups
gcloud sql backups list --instance=resume-db
```

## ❌ Troubleshooting

### Common Issues:

1. **Billing not enabled**: Enable billing in Google Cloud Console
2. **Services not enabled**: Run the service enable commands
3. **Database connection**: Check connection string format
4. **Memory errors**: Increase memory allocation in app.yaml
5. **Build failures**: Check requirements.txt for conflicts

### Getting Help:
```bash
# Check deployment status
gcloud app describe  # for App Engine
gcloud run services describe resume-match-ai --region us-central1  # for Cloud Run

# View detailed logs
gcloud app logs read --severity=ERROR
```

## 🎯 Next Steps After Deployment

1. **Test the application** with sample data
2. **Set up monitoring** and alerts
3. **Configure custom domain** (optional)
4. **Set up CI/CD pipeline** for automatic deployments
5. **Enable database backups** schedule

## 📞 Support Resources

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Community Support**: https://stackoverflow.com/questions/tagged/google-cloud-platform  
- **Official Support**: Available with paid support plans