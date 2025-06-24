# Deploy Resume Match AI to Google Cloud Platform

## Prerequisites

1. **Google Cloud Account**: Create one at https://cloud.google.com
2. **Google Cloud CLI**: Install from https://cloud.google.com/sdk/docs/install
3. **Project Setup**: Create a new Google Cloud project

## Step-by-Step Deployment

### 1. Set Up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (replace PROJECT_ID with your chosen name)
gcloud projects create resume-match-ai-PROJECT_ID

# Set the project as default
gcloud config set project resume-match-ai-PROJECT_ID

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

### 2. Set Up Cloud SQL PostgreSQL Database

```bash
# Create a PostgreSQL instance
gcloud sql instances create resume-match-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Create a database
gcloud sql databases create resumematchai --instance=resume-match-db

# Create a user
gcloud sql users create appuser --instance=resume-match-db --password=YOUR_SECURE_PASSWORD

# Get the connection string
gcloud sql instances describe resume-match-db --format="value(connectionName)"
```

### 3. Configure Environment Variables

Create a file called `.env.yaml` with your database connection:

```yaml
env_variables:
  DATABASE_URL: "postgresql://appuser:YOUR_SECURE_PASSWORD@/resumematchai?host=/cloudsql/YOUR_PROJECT_ID:us-central1:resume-match-db"
  SESSION_SECRET: "your-super-secret-session-key-here"
```

### 4. Initialize App Engine

```bash
# Initialize App Engine in your project
gcloud app create --region=us-central1
```

### 5. Deploy the Application

```bash
# Deploy using the configuration files
gcloud app deploy app.yaml --env-vars-file=.env.yaml
```

### 6. Access Your Application

```bash
# Open your deployed application
gcloud app browse
```

## Important Configuration Notes

### Database Connection
- The app uses Cloud SQL Proxy for secure database connections
- Connection string format: `postgresql://user:password@/database?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME`

### File Uploads
- App Engine has a 32MB request size limit
- Consider using Cloud Storage for larger file uploads in production

### Scaling
- The app.yaml configures automatic scaling (1-10 instances)
- Adjust `max_instances` based on expected traffic

### Costs
- F1-micro database tier: ~$7-10/month
- App Engine: Pay-per-use (free tier available)
- Estimated cost for low traffic: $10-20/month

## Security Recommendations

1. **Database Security**: Use strong passwords and enable SSL
2. **Environment Variables**: Never commit `.env.yaml` to version control
3. **Access Control**: Set up IAM roles for team access
4. **HTTPS**: App Engine automatically provides SSL certificates

## Monitoring and Logs

```bash
# View application logs
gcloud app logs tail -s default

# View error logs
gcloud app logs read --severity=ERROR
```

## Updating the Application

To update your deployed application:

```bash
# Make your changes, then redeploy
gcloud app deploy app.yaml --env-vars-file=.env.yaml
```

## Troubleshooting

### Common Issues:
1. **Database Connection Errors**: Check your connection string format
2. **Module Import Errors**: Ensure all dependencies are in requirements-gcp.txt
3. **Memory Errors**: Increase memory allocation in app.yaml if needed

### Getting Help:
- Check logs: `gcloud app logs tail`
- Google Cloud Console: https://console.cloud.google.com
- Support: Google Cloud Support (paid plans)