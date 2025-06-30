# Google Cloud Run PORT Variable Fix

## 🚨 Problem
Google Cloud Run automatically sets the `PORT` environment variable and doesn't allow manual override. The error "This name is reserved" occurs when trying to set PORT manually.

## ✅ Solution
Remove the PORT environment variable from your Cloud Run configuration. Cloud Run will automatically set it to 8080.

## 🔧 Steps to Fix

### In Cloud Run Console:
1. **Remove the PORT variable** from environment variables
2. **Keep only these variables**:
   ```
   DATABASE_URL=postgresql://...
   SESSION_SECRET=your-secret-key
   FLASK_ENV=production
   ```
3. **Deploy** - Cloud Run will automatically set PORT=8080

### Why This Works:
- Cloud Run automatically injects `PORT=8080` 
- Your Dockerfile is already configured to read `${PORT:-8080}`
- App will automatically bind to the correct port

## 🎯 Final Environment Variables
Only set these in Cloud Run:
```
DATABASE_URL=postgresql://username:password@host:5432/database
SESSION_SECRET=your-long-random-secret-key
FLASK_ENV=production
```

**Do NOT set PORT** - Cloud Run handles this automatically.

## 🚀 Deploy Now
After removing the PORT variable, click Deploy. The deployment should succeed.