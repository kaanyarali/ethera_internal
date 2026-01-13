# Fix Firebase Storage Permissions

## Problem
Your service account doesn't have permission to access the Firebase Storage bucket `ethera-images`.

**Error:**
```
403: 464295668478-compute@developer.gserviceaccount.com does not have storage.buckets.get access
```

## Solution: Grant Storage Permissions

### Option 1: Using Google Cloud Console (Recommended)

1. **Go to Google Cloud Console IAM:**
   - Visit: https://console.cloud.google.com/iam-admin/iam?project=project-2799141d-0677-4078-a07
   - Or: Google Cloud Console > IAM & Admin > IAM

2. **Find your service account:**
   - Look for: `464295668478-compute@developer.gserviceaccount.com`
   - Or search for "compute@developer"

3. **Edit the service account:**
   - Click the pencil icon (Edit) next to the service account

4. **Add Storage Admin role:**
   - Click "ADD ANOTHER ROLE"
   - Select: **Storage Admin** (or **Storage Object Admin** for more limited access)
   - Click "SAVE"

### Option 2: Using gcloud CLI

```bash
# Grant Storage Admin role to the service account
gcloud projects add-iam-policy-binding project-2799141d-0677-4078-a07 \
    --member="serviceAccount:464295668478-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin"
```

Or for more limited access (only object operations):

```bash
# Grant Storage Object Admin role
gcloud projects add-iam-policy-binding project-2799141d-0677-4078-a07 \
    --member="serviceAccount:464295668478-compute@developer.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### Option 3: Bucket-Level Permissions (If bucket exists in different project)

If the bucket `ethera-images` is in a different project, you need to grant permissions on the bucket itself:

1. **Go to Cloud Storage:**
   - Visit: https://console.cloud.google.com/storage/browser?project=project-2799141d-0677-4078-a07
   - Find the bucket `ethera-images`

2. **Edit bucket permissions:**
   - Click on the bucket name
   - Go to "Permissions" tab
   - Click "ADD PRINCIPAL"
   - Enter: `464295668478-compute@developer.gserviceaccount.com`
   - Select role: **Storage Admin** or **Storage Object Admin**
   - Click "SAVE"

## Verify the Bucket Name

If you're not sure about the bucket name:

1. **Go to Firebase Console:**
   - Visit: https://console.firebase.google.com/project/project-2799141d-0677-4078-a07/storage
   - The bucket name is shown at the top of the Storage page

2. **Check in Google Cloud Console:**
   - Visit: https://console.cloud.google.com/storage/browser?project=project-2799141d-0677-4078-a07
   - You'll see all storage buckets for your project

## After Fixing Permissions

1. **Restart your local server** (if running)
2. **Try uploading an image again**
3. You should see: `✓ Firebase Storage bucket initialized: ethera-images`

## Required Roles

- **Storage Admin**: Full control over buckets and objects (recommended for development)
- **Storage Object Admin**: Can create, delete, and update objects (but not manage buckets)
- **Storage Object Creator**: Can only create objects (limited)

For this application, **Storage Admin** or **Storage Object Admin** is recommended.
