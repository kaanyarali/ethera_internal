# Make Firebase Storage Bucket Public

## Problem
Images are showing "Access Denied" errors because the bucket is not publicly accessible.

## Solution: Make Bucket Public

### Option 1: Using Google Cloud Console (Recommended)

1. **Go to Cloud Storage:**
   - Visit: https://console.cloud.google.com/storage/browser?project=project-2799141d-0677-4078-a07
   - Or: Google Cloud Console > Cloud Storage > Buckets

2. **Select your bucket:**
   - Click on the bucket name: `ethera-images`

3. **Go to Permissions tab:**
   - Click on the "Permissions" tab at the top

4. **Make bucket public:**
   - Click "ADD PRINCIPAL"
   - In "New principals", enter: `allUsers`
   - In "Select a role", choose: **Storage Object Viewer**
   - Click "SAVE"

5. **Confirm the warning:**
   - You'll see a warning about making the bucket public
   - Click "ALLOW PUBLIC ACCESS"

### Option 2: Using gcloud CLI

```bash
# Grant public read access to the bucket
gsutil iam ch allUsers:objectViewer gs://ethera-images
```

### Option 3: Using Bucket Policy (Alternative)

If you want more control, you can set a bucket policy that allows public read access:

1. Go to Cloud Storage > Buckets > ethera-images
2. Click "Edit bucket"
3. Go to "Permissions" tab
4. Add principal: `allUsers` with role: `Storage Object Viewer`

## Verify

After making the bucket public:
1. Try accessing an image URL directly in your browser
2. The image should load without authentication
3. Images in your product detail pages should display correctly

## Security Note

⚠️ **Making a bucket public means anyone with the URL can access the files.**

For production, consider:
- Using signed URLs (already implemented in the code)
- Restricting access to specific paths
- Using Firebase Storage security rules

However, for product images that should be publicly viewable, making the bucket public is acceptable.
