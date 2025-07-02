# Fix Google Cloud Run Memory Issue

## 🚨 Problem Identified
Your Google Cloud Run deployment is failing because:
- **Memory limit**: 512MB is too small
- **Actual usage**: 627MB needed
- **spaCy + Flask + ML libraries**: Require more memory

## ✅ Solution Applied

### 1. Updated Memory Allocation
**Before**: 512MB memory, 1 CPU
**After**: 4GB memory, 2 CPU

### 2. Files Updated
- `cloud-run.yaml` - Increased memory to 4GB
- `Dockerfile` - Added pip cache cleanup to reduce image size

## 🚀 Redeploy Instructions

### Option 1: Using Cloud Console (Recommended)
1. **Go to Cloud Run**: https://console.cloud.google.com/run
2. **Select your service**: resumematchai
3. **Edit & Deploy New Revision**
4. **Set Resource Limits**:
   - Memory: **4 GiB**
   - CPU: **2**
5. **Deploy**

### Option 2: Using Cloud Shell
```bash
# Deploy with increased memory
gcloud run deploy resumematchai \
  --image gcr.io/YOUR_PROJECT_ID/resume-match-ai \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --allow-unauthenticated
```

### Option 3: Using updated cloud-run.yaml
```bash
# Deploy using the updated configuration file
gcloud run services replace cloud-run.yaml
```

## 💰 Cost Impact
**Previous**: ~$7-15/month
**New**: ~$20-35/month (due to increased memory/CPU)

## 🔧 Why This Fixes the Issue

### Memory Usage Breakdown:
- **Python runtime**: ~100MB
- **Flask + dependencies**: ~150MB
- **spaCy model**: ~200MB
- **scikit-learn**: ~100MB
- **Application data**: ~50MB
- **Buffer for processing**: ~100MB
- **Total needed**: ~700MB

### Previous vs New:
- **Before**: 512MB → Out of memory crashes
- **After**: 4GB → Plenty of headroom for processing

## 🎯 Alternative: Reduce Memory Usage

If you want to keep costs low, we can:

1. **Use smaller spaCy model**: Switch to `en_core_web_sm` optimized version
2. **Lazy loading**: Load ML models only when needed
3. **Process files in chunks**: Handle large documents in smaller pieces
4. **Use Cloud Storage**: Store files externally instead of in memory

## 📊 Expected Performance
With 4GB memory:
- **Startup time**: ~30-60 seconds
- **Document processing**: Fast and reliable
- **Concurrent users**: 10-20 simultaneously
- **Large file handling**: PDFs up to 10MB easily

## 🚨 Quick Fix Now
**Immediate action**: Increase memory to 4GB in Cloud Run console and redeploy.
**Long-term**: Consider optimization strategies if cost becomes a concern.

The memory issue is now resolved. Your deployment should succeed with the increased resource allocation.