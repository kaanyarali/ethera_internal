# Local Testing Guide

This guide will help you test the application locally before deploying to Cloud Run.

## Prerequisites

1. **Python 3.9+** installed
2. **Firebase project** set up with Firestore and Storage enabled
3. **Service account key** downloaded from Firebase Console

## Step 1: Activate Virtual Environment

```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

## Step 2: Install Dependencies (if not already installed)

```bash
pip install -r requirements.txt
```

## Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following to `.env`:

```env
# Path to your Firebase service account JSON file (absolute path)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-service-account-key.json

# Your Firebase Storage bucket name
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

# Optional: GCP Project ID (if different from service account)
GCP_PROJECT_ID=your-project-id

# Optional: Firestore Database ID (defaults to "(default)" if not set)
FIRESTORE_DATABASE_ID=(default)
```

**Example `.env` file:**
```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/kaanyarali/Downloads/ethera-jewelry-firebase-adminsdk-xxxxx.json
FIREBASE_STORAGE_BUCKET=ethera-jewelry-12345.appspot.com
GCP_PROJECT_ID=ethera-jewelry-12345
FIRESTORE_DATABASE_ID=(default)
```

## Step 4: Get Your Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click the gear icon ⚙️ > **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate new private key**
6. Save the JSON file and note its path
7. Copy the path to `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` file

## Step 5: Get Your Storage Bucket Name

1. In Firebase Console, go to **Build** > **Storage**
2. Look at the top - you'll see your bucket name (e.g., `your-project-id.appspot.com`)
3. Copy it to `FIREBASE_STORAGE_BUCKET` in your `.env` file

## Step 6: Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes (useful for development).

## Step 7: Access the Application

Open your browser and go to:
- **Home**: http://localhost:8000
- **Materials**: http://localhost:8000/materials
- **Purchases**: http://localhost:8000/purchases
- **Products**: http://localhost:8000/products
- **Dashboard**: http://localhost:8000/dashboard

## Testing Checklist

- [ ] Application starts without errors
- [ ] Can view materials list
- [ ] Can create a new material
- [ ] Can view purchases list
- [ ] Can create a new purchase
- [ ] Can view products list
- [ ] Can create a new product with multiple images
- [ ] Images upload successfully to Firebase Storage
- [ ] Dashboard loads and shows charts
- [ ] Cost estimation works correctly

## Troubleshooting

### Error: "Firebase Admin SDK initialization error"
- Check that `GOOGLE_APPLICATION_CREDENTIALS` path is correct and absolute
- Verify the JSON file exists and is valid
- Make sure the path doesn't have spaces (use quotes if needed)

### Error: "Firestore client initialization failed"
- Check that Firestore is enabled in Firebase Console
- Verify `GCP_PROJECT_ID` matches your Firebase project ID
- Check that `FIRESTORE_DATABASE_ID` is correct (usually "(default)")

### Error: "Could not initialize Firebase Storage bucket"
- Verify `FIREBASE_STORAGE_BUCKET` is set correctly
- Check that Storage is enabled in Firebase Console
- Make sure the bucket name includes `.appspot.com`

### Images not uploading
- Check that `FIREBASE_STORAGE_BUCKET` is set in `.env`
- Verify Storage rules allow uploads (check Firebase Console > Storage > Rules)
- Check browser console for errors

### Port already in use
If port 8000 is already in use, use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

## Next Steps

Once local testing is successful:
1. Test all features thoroughly
2. Verify data is being saved to Firestore
3. Check that images are uploaded to Firebase Storage
4. Test the dashboard and cost calculations
5. When ready, deploy to Cloud Run (see `CLOUD_RUN_DEPLOYMENT.md`)
