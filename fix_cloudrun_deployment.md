# Fix Google Cloud Run Deployment - Port Issue Resolved

## 🔧 Problem Fixed

The deployment failed because Google Cloud Run expects apps to listen on port **8080**, but your Flask app was configured for port **5000**.

## ✅ Changes Made

### 1. Updated Dockerfile
- Changed port from 5000 to 8080
- Added PORT environment variable support
- Updated health checks to use dynamic port

### 2. Updated cloud-run.yaml
- Set containerPort to 8080
- Added PORT environment variable
- Updated health check probes

## 🚀 Quick Redeploy Steps

### Option 1: Using gcloud CLI
```bash
# Rebuild and deploy with fixes
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/resume-match-ai
gcloud run deploy resumematchai \
  --image gcr.io/YOUR_PROJECT_ID/resume-match-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars PORT=8080
```

### Option 2: Using Cloud Console
1. **Go to Cloud Run**: https://console.cloud.google.com/run
2. **Select your service**: resumematchai
3. **Edit & Deploy New Revision**
4. **Set Environment Variables**:
   ```
   PORT=8080
   DATABASE_URL=your-database-url
   SESSION_SECRET=your-secret-key
   ```
5. **Deploy**

## 🔍 What Changed in Files

### Dockerfile Changes:
```dockerfile
# Before (old)
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", ...]

# After (fixed)
EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} ...
```

### cloud-run.yaml Changes:
```yaml
# Before (old)
ports:
- containerPort: 5000

# After (fixed)
ports:
- containerPort: 8080
env:
- name: PORT
  value: "8080"
```

## 💡 Why This Happens

**Google Cloud Run Requirements:**
- Must listen on port specified by `PORT` environment variable
- Default PORT is 8080 if not specified
- Container must start within timeout period (default 240 seconds)
- Must respond to HTTP requests on the specified port

**Your Original Setup:**
- Flask app hardcoded to port 5000
- Cloud Run was setting PORT=8080
- App ignored Cloud Run's PORT variable
- Health checks failed → deployment failed

## ✅ Now Your App Will:
1. **Read PORT environment variable** (8080 on Cloud Run)
2. **Listen on correct port** automatically
3. **Pass health checks** 
4. **Deploy successfully**

## 🔄 Alternative: Use Railway Instead

If you prefer to avoid Google Cloud Run complexity:

```bash
# Railway automatically handles ports
# No configuration needed - just push to GitHub
# Connect repository → automatic deployment
```

Railway is more beginner-friendly and handles these port configurations automatically.

## 🚨 Environment Variables Needed

Make sure these are set in Cloud Run:
```bash
PORT=8080
DATABASE_URL=postgresql://user:pass@host:5432/db
SESSION_SECRET=your-long-random-secret
FLASK_ENV=production
```

Your deployment should now work correctly with these fixes!