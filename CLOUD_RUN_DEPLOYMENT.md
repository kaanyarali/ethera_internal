# Cloud Run Deployment Guide

This guide explains how to deploy Ethera Jewelry to Google Cloud Run.

## Prerequisites

1. Google Cloud Project with billing enabled
2. Firebase project (same or different from GCP project)
3. `gcloud` CLI installed and authenticated
4. Docker installed (for local testing)

## Step 1: Set Up Firebase

1. Create a Firebase project (or use existing)
2. Enable **Firestore Database**
3. Enable **Firebase Storage**
4. Note your **Storage bucket name** (format: `your-project-id.appspot.com`)

## Step 2: Create Dockerfile

The Dockerfile is already created. It:
- Uses Python 3.11
- Installs dependencies
- Runs the FastAPI app on port 8080

## Step 3: Build and Deploy

### Option A: Deploy from Local Machine

```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id
export SERVICE_NAME=ethera-jewelry
export REGION=us-central1

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_STORAGE_BUCKET=your-firebase-project-id.appspot.com \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

### Option B: Deploy from Cloud Build (Recommended)

1. Create `cloudbuild.yaml` in project root
2. Push code to Cloud Source Repositories or GitHub
3. Connect to Cloud Build trigger

## Step 4: Set Environment Variables in Cloud Run

**Important:** For Cloud Run, you do NOT need `GOOGLE_APPLICATION_CREDENTIALS` because Cloud Run automatically provides default credentials.

You only need to set:

### Required Environment Variable:
- `FIREBASE_STORAGE_BUCKET` - Your Firebase Storage bucket name

### How to Set Environment Variables:

**Via gcloud CLI:**
```bash
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --set-env-vars FIREBASE_STORAGE_BUCKET=your-firebase-project-id.appspot.com
```

**Via Cloud Console:**
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service
3. Click "Edit & Deploy New Revision"
4. Go to "Variables & Secrets" tab
5. Add environment variable:
   - Name: `FIREBASE_STORAGE_BUCKET`
   - Value: `your-firebase-project-id.appspot.com`
6. Click "Deploy"

## Step 5: Configure Service Account Permissions

Cloud Run uses a service account. Make sure it has permissions:

1. Go to Cloud Run > Your Service > Permissions tab
2. The default service account is: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
3. Grant these roles:
   - **Cloud Datastore User** (for Firestore)
   - **Storage Object Admin** (for Firebase Storage)

Or via gcloud:
```bash
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export SERVICE_ACCOUNT=$PROJECT_NUMBER-compute@developer.gserviceaccount.com

# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

# Grant Storage access (if using same project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"
```

**If Firebase is in a different project:**
- Grant the Cloud Run service account access to the Firebase project
- Or use a custom service account with cross-project access

## Step 6: Test Deployment

1. Get your service URL:
```bash
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
```

2. Visit the URL in your browser
3. Test the application

## Environment Variables Summary

### Local Development:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

### Cloud Run:
```env
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
# GOOGLE_APPLICATION_CREDENTIALS is NOT needed - uses default credentials
```

## Troubleshooting

### Error: "Permission denied" accessing Firestore
- Check service account has "Cloud Datastore User" role
- Verify Firebase project allows access from GCP project

### Error: "Could not initialize Firebase Storage bucket"
- Verify `FIREBASE_STORAGE_BUCKET` is set correctly
- Check bucket name format: `project-id.appspot.com`
- Ensure Storage is enabled in Firebase

### Error: "Default credentials not found"
- Cloud Run should automatically provide credentials
- If using custom service account, ensure it's set in Cloud Run service settings

## Continuous Deployment

Set up Cloud Build for automatic deployments:

1. Create `cloudbuild.yaml`:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ethera-jewelry', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ethera-jewelry']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'ethera-jewelry'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ethera-jewelry'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
images:
  - 'gcr.io/$PROJECT_ID/ethera-jewelry'
```

2. Connect to GitHub/Cloud Source Repositories
3. Create Cloud Build trigger

## Cost Optimization

- Set `--min-instances 0` to scale to zero (saves money)
- Adjust `--memory` and `--cpu` based on usage
- Set `--max-instances` to limit costs
- Use Cloud Run's free tier (2 million requests/month)
