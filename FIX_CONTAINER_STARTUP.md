# Fix: Container Failed to Start on Port 8080

If you're getting this error:
```
The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable
```

This means your container is crashing before it can start listening on port 8080.

## Common Causes & Solutions

### 1. Firebase Initialization Failing (Most Common)

**Symptom:** Container crashes immediately on startup  
**Cause:** Firebase/Firestore initialization errors (permissions, missing project ID, etc.)

**Solution:**
1. Check Cloud Run logs for the actual error
2. Make sure you've set these environment variables:
   - `GCP_PROJECT_ID=project-2799141d-0677-4078-a07`
   - `FIRESTORE_DATABASE_ID=(default)`
3. Grant Firestore permissions (see `FIX_PERMISSIONS.md`)

### 2. Missing Environment Variables

**Solution:** Set required environment variables in Cloud Run:
- `GCP_PROJECT_ID` - Your GCP project ID
- `FIRESTORE_DATABASE_ID` - Usually `(default)`
- `FIREBASE_STORAGE_BUCKET` - If using images

### 3. Import Errors

**Symptom:** Python import errors in logs  
**Solution:** Check that all dependencies are in `requirements.txt`

### 4. Port Configuration Issue

**Solution:** The Dockerfile is already configured correctly. Make sure:
- Cloud Run is using the default port (8080)
- Don't override PORT environment variable

## Quick Fix Steps

### Step 1: Check Logs

1. Go to [Cloud Run Logs](https://console.cloud.google.com/run)
2. Click on your service
3. Click "Logs" tab
4. Look for the actual error message

### Step 2: Set Required Environment Variables

In Cloud Run Console → Your Service → Edit & Deploy New Revision → Variables & Secrets:

```
GCP_PROJECT_ID=project-2799141d-0677-4078-a07
FIRESTORE_DATABASE_ID=(default)
```

### Step 3: Grant Permissions

Follow `FIX_PERMISSIONS.md` to grant Firestore access to your service account.

### Step 4: Increase Startup Timeout (if needed)

1. In Cloud Run Console → Your Service → Edit
2. Go to "Container" tab
3. Increase "Startup CPU boost" if available
4. Or increase timeout in "Container startup timeout"

### Step 5: Test Locally First

Before deploying, test the container locally:

```bash
# Build the image
docker build -t ethera-jewelry .

# Run locally
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=project-2799141d-0677-4078-a07 \
  -e FIRESTORE_DATABASE_ID="(default)" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  ethera-jewelry
```

If it works locally but not in Cloud Run, it's likely a permissions issue.

## Debugging Commands

### Check if container starts locally:
```bash
docker build -t test-app .
docker run --rm -p 8080:8080 test-app
```

### Check Cloud Run service details:
```bash
gcloud run services describe ethera-internal \
  --region europe-west1 \
  --format="yaml(spec.template.spec.containers[0].env)"
```

## Most Likely Issue

Based on your previous errors, the most likely cause is:
1. **Missing `GCP_PROJECT_ID` environment variable** - Set this!
2. **Missing Firestore permissions** - Grant `roles/datastore.user` role

Fix these two things first, then redeploy.
