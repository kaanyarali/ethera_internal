# Fix: 403 Missing or Insufficient Permissions

If you're getting this error:
```
google.api_core.exceptions.PermissionDenied: 403 Missing or insufficient permissions.
```

Your Cloud Run service account doesn't have permission to access Firestore.

## Quick Fix

### Option 1: Via Cloud Console (Easiest)

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service name
3. Click **"Edit & Deploy New Revision"**
4. Go to **"Security"** tab
5. Under **"Service account"**, note which service account is being used
   - Default: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
6. Click **"Show Advanced Settings"** if needed
7. Save (you don't need to change anything here, just note the service account)

8. Now go to [IAM & Admin](https://console.cloud.google.com/iam-admin/iam)
9. Find the service account (from step 5)
10. Click the **pencil icon** (Edit) next to it
11. Click **"Add Another Role"**
12. Add these roles:
    - **Cloud Datastore User** (for Firestore access)
    - **Storage Object Admin** (for Firebase Storage, if using images)
13. Click **"Save"**

### Option 2: Via gcloud CLI

```bash
# Set your project ID
export PROJECT_ID=project-2799141d-0677-4078-a07

# Get your project number
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Set the service account (default Cloud Run service account)
export SERVICE_ACCOUNT=$PROJECT_NUMBER-compute@developer.gserviceaccount.com

# Grant Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

# Grant Storage access (if using Firebase Storage for images)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"
```

### Option 3: If Firebase is in a Different Project

If your Firebase project is different from your GCP project:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your Firebase project
3. Go to **Project Settings** (gear icon) > **Users and permissions**
4. Click **"Add member"**
5. Add the Cloud Run service account email: `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
6. Grant role: **Editor** or **Firebase Admin**
7. Click **"Add"**

## Verify Permissions

After granting permissions, wait 1-2 minutes for them to propagate, then:

1. Try accessing your Cloud Run service again
2. The error should be resolved

## Required Roles Summary

| Role | Purpose | Required For |
|------|---------|--------------|
| `roles/datastore.user` | Firestore read/write access | ✅ Always needed |
| `roles/storage.objectAdmin` | Firebase Storage access | Only if uploading images |

## Troubleshooting

**Still getting permission errors?**
- Wait 2-3 minutes for permissions to propagate
- Make sure you're granting permissions to the correct service account
- Check that the service account email matches what's shown in Cloud Run

**Can't find the service account?**
- In Cloud Run, go to your service > Security tab
- The service account email is shown there
- Copy it exactly (including the `@developer.gserviceaccount.com` part)
