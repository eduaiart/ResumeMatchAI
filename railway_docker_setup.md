# Railway Docker Deployment - Step by Step

## 🚀 Deploy Your Resume Match AI to Railway Using Docker

Railway automatically detects and uses your Dockerfile for deployment. Here's the complete guide:

## Prerequisites
- GitHub account
- Your Resume Match AI code in a GitHub repository

## Step 1: Prepare Your Repository

Your repository should contain these key files:
```
├── Dockerfile                 ✅ (Already created)
├── requirements-appengine.txt ✅ (Already created)  
├── main.py                   ✅ (Your Flask app)
├── models.py                 ✅ (Database models)
├── routes.py                 ✅ (Application routes)
├── templates/                ✅ (HTML templates)
├── static/                   ✅ (CSS/JS files)
└── ... (other Python files)
```

## Step 2: Deploy to Railway

### 2.1 Sign Up and Connect GitHub
1. Go to **https://railway.app**
2. Click **"Login"** and sign up with GitHub
3. Grant Railway access to your repositories

### 2.2 Deploy Your Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **resume-match-ai** repository
4. Railway will automatically:
   - Detect your Dockerfile
   - Build the Docker image
   - Deploy your application

## Step 3: Add PostgreSQL Database

### 3.1 Add Database Service
1. In your Railway project dashboard
2. Click **"+ New Service"**
3. Select **"Database" → "PostgreSQL"**
4. Railway creates and configures the database automatically

### 3.2 Get Database Connection
1. Click on your **PostgreSQL service**
2. Go to **"Variables"** tab
3. Copy the **DATABASE_URL** (it looks like this):
   ```
   postgresql://postgres:password@host:5432/railway
   ```

## Step 4: Configure Environment Variables

### 4.1 Set Application Variables
1. Click on your **web service** (resume-match-ai)
2. Go to **"Variables"** tab
3. Add these variables:

```bash
DATABASE_URL=postgresql://postgres:generated-password@postgres:5432/railway
SESSION_SECRET=your-random-secret-key-make-it-long-and-secure
FLASK_ENV=production
PORT=5000
```

**Note**: Railway automatically provides the DATABASE_URL when you add PostgreSQL service.

### 4.2 Generate Session Secret
Use this command to generate a secure session secret:
```bash
openssl rand -base64 32
```
Or use any long random string (32+ characters).

## Step 5: Verify Deployment

### 5.1 Check Build Logs
1. In Railway dashboard, click on your web service
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. Check **"Build Logs"** for any errors

### 5.2 Check Runtime Logs
1. Go to **"Logs"** tab
2. Look for successful startup messages:
   ```
   INFO:root:spaCy model loaded successfully
   [INFO] Starting gunicorn
   [INFO] Listening at: http://0.0.0.0:5000
   ```

### 5.3 Access Your Application
1. In Railway dashboard, you'll see a **URL** for your service
2. Click the URL to access your application
3. Test by uploading a job description and resume

## Step 6: Custom Domain (Optional)

### 6.1 Add Custom Domain
1. In your web service settings
2. Go to **"Domains"** tab
3. Click **"+ Custom Domain"**
4. Enter your domain name
5. Update your DNS settings as instructed

## 🔧 Troubleshooting

### Common Issues:

**Build Failures:**
- Check if all files are committed to GitHub
- Verify Dockerfile syntax
- Check build logs for specific errors

**Database Connection Errors:**
- Ensure PostgreSQL service is running
- Verify DATABASE_URL format
- Check if database and app are in same project

**Application Won't Start:**
- Check if PORT environment variable is set to 5000
- Verify all Python dependencies in requirements file
- Check runtime logs for Python errors

**Memory/Resource Issues:**
- Railway provides 512MB RAM by default
- Upgrade plan if you need more resources
- Optimize your application for memory usage

### Debug Commands:
Railway provides these useful features:
- **Real-time logs** in dashboard
- **Metrics** showing CPU/memory usage  
- **Environment variables** management
- **Rollback** to previous deployments

## 💰 Railway Pricing

### Hobby Plan (Free):
- $5 in credits monthly
- 512MB RAM, 1 vCPU
- Perfect for testing and small projects

### Pro Plan ($20/month):
- $20 in credits monthly  
- Higher resource limits
- Custom domains included
- Priority support

## 🎯 Advantages of Railway + Docker

1. **Zero Configuration**: Railway detects Dockerfile automatically
2. **Integrated Database**: PostgreSQL included with one click
3. **Environment Variables**: Easy management via dashboard
4. **Git Integration**: Deploy on every push to main branch
5. **Scaling**: Easy to scale up resources as needed
6. **Monitoring**: Built-in logs and metrics
7. **Custom Domains**: Free SSL certificates included

## 📊 Expected Performance

With your Docker setup on Railway:
- **Build time**: 3-5 minutes (first deployment)
- **Subsequent deploys**: 1-2 minutes
- **Memory usage**: ~200-400MB
- **Response time**: <500ms for typical requests

Your Resume Match AI application will be production-ready with automatic scaling, database backups, and monitoring included.