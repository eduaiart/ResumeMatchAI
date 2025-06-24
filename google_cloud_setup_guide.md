# Complete Google Cloud Setup Guide for Beginners

## What is Google Cloud Platform (GCP)?
Google Cloud Platform is Google's cloud computing service that lets you run your web applications on Google's infrastructure. It's similar to how you use Replit, but for production websites that can handle real users.

## Step 1: Create Your Google Cloud Account

### 1.1 Sign Up
1. Go to https://cloud.google.com
2. Click "Get started for free"
3. Sign in with your Google account (or create one)
4. You'll get $300 in free credits (valid for 90 days)
5. Enter your credit card (required, but you won't be charged during free trial)

### 1.2 Accept Terms and Complete Setup
- Accept the terms of service
- Verify your identity
- Choose your country/region

## Step 2: Install Google Cloud CLI (Command Line Interface)

### For Windows:
1. Download from: https://cloud.google.com/sdk/docs/install-sdk#windows
2. Run the installer
3. Follow the setup wizard
4. Open Command Prompt or PowerShell as Administrator

### For Mac:
1. Open Terminal
2. Run: `curl https://sdk.cloud.google.com | bash`
3. Restart Terminal
4. Run: `gcloud init`

### For Linux:
1. Open Terminal
2. Run: `curl https://sdk.cloud.google.com | bash`
3. Restart Terminal
4. Run: `gcloud init`

## Step 3: Set Up Your First Project

### 3.1 Create a Project
```bash
# Login to Google Cloud (this will open a browser)
gcloud auth login

# Create a new project (replace "my-resume-app" with your preferred name)
gcloud projects create my-resume-app-12345

# Set this project as your default
gcloud config set project my-resume-app-12345

# Check if it worked
gcloud config get-value project
```

**Important**: Project names must be globally unique. Add numbers or your name to make it unique.

### 3.2 Enable Billing
1. Go to https://console.cloud.google.com
2. Select your project from the dropdown at the top
3. Go to "Billing" in the left menu
4. Link your project to your billing account

## Step 4: Enable Required Services

```bash
# Enable App Engine (for hosting your website)
gcloud services enable appengine.googleapis.com

# Enable Cloud SQL (for your database)
gcloud services enable sqladmin.googleapis.com

# Enable Cloud Build (for automatic deployment)
gcloud services enable cloudbuild.googleapis.com

# Check if services are enabled
gcloud services list --enabled
```

## Step 5: Create Your Database

### 5.1 Create PostgreSQL Instance
```bash
# Create a small database server (this will take 5-10 minutes)
gcloud sql instances create resume-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --storage-size=10GB \
    --storage-type=SSD
```

**What this does**: Creates a small PostgreSQL database server in Google's data center.

### 5.2 Create Database and User
```bash
# Create the actual database
gcloud sql databases create resumematchai --instance=resume-db

# Create a user for your app (replace YOUR_PASSWORD with a strong password)
gcloud sql users create appuser \
    --instance=resume-db \
    --password=YourStrongPassword123!

# Get your database connection info (save this!)
gcloud sql instances describe resume-db --format="value(connectionName)"
```

**Save the output** - you'll need it later!

## Step 6: Initialize App Engine

```bash
# Initialize App Engine in us-central1 region
gcloud app create --region=us-central1
```

**What this does**: Sets up the web hosting service for your application.

## Step 7: Create Environment Configuration

Create a file called `.env.yaml` in your project folder with this content:

```yaml
env_variables:
  DATABASE_URL: "postgresql://appuser:YourStrongPassword123!@/resumematchai?host=/cloudsql/YOUR_PROJECT_ID:us-central1:resume-db"
  SESSION_SECRET: "your-super-secret-key-here-make-it-long-and-random"
```

**Replace**:
- `YourStrongPassword123!` with your actual password
- `YOUR_PROJECT_ID` with your project ID (like `my-resume-app-12345`)

## Step 8: Deploy Your Application

```bash
# Navigate to your project folder
cd /path/to/your/resume-match-ai

# Deploy your application
gcloud app deploy app.yaml --env-vars-file=.env.yaml

# When prompted, type 'Y' to continue
```

This will take 10-15 minutes for the first deployment.

## Step 9: View Your Live Application

```bash
# Open your deployed application in browser
gcloud app browse
```

## Cost Breakdown (Beginner-Friendly)

### Free Tier (Always Free):
- App Engine: 28 hours per day free
- Cloud SQL: First 30 days free with credits

### After Free Credits:
- **Database (db-f1-micro)**: ~$7-10/month
- **App Engine**: ~$5-15/month for low traffic
- **Total estimated**: $12-25/month for a small business

### Cost-Saving Tips:
1. Use `db-f1-micro` tier (smallest/cheapest)
2. Set up budget alerts
3. Stop instances when not needed

## Common Beginner Mistakes to Avoid

1. **Forgetting to enable billing**: Your app won't deploy without it
2. **Using weak passwords**: Use strong database passwords
3. **Not saving connection strings**: Write down your database info
4. **Choosing wrong regions**: Stick with `us-central1` for lowest costs
5. **Not setting up monitoring**: Enable logging to catch issues early

## Getting Help

### If Something Goes Wrong:
```bash
# View your app logs
gcloud app logs tail

# Check app status
gcloud app describe
```

### Useful Google Cloud Console Pages:
- Dashboard: https://console.cloud.google.com
- App Engine: https://console.cloud.google.com/appengine
- SQL: https://console.cloud.google.com/sql
- Billing: https://console.cloud.google.com/billing

## Next Steps After Deployment

1. **Test your application**: Upload a job and some resumes
2. **Set up monitoring**: Enable error reporting
3. **Configure domain**: Add your custom domain name
4. **Set up backups**: Schedule database backups

## Emergency Commands

```bash
# Stop your app (to save money)
gcloud app versions stop [VERSION]

# Delete your database (careful!)
gcloud sql instances delete resume-db

# Delete your entire project
gcloud projects delete PROJECT_ID
```

## Need More Help?

1. **Google Cloud Documentation**: https://cloud.google.com/docs
2. **Community Support**: https://stackoverflow.com/questions/tagged/google-cloud-platform
3. **YouTube Tutorials**: Search "Google Cloud App Engine tutorial"