# Firebase Setup Guide

This guide will help you set up Firebase for the Ethera Jewelry application.

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard:
   - Enter project name (e.g., "ethera-jewelry")
   - Enable/disable Google Analytics (optional)
   - Click "Create project"

## Step 2: Enable Firestore Database

1. In Firebase Console, go to **Build** > **Firestore Database**
2. Click "Create database"
3. Choose **Production mode** (or Test mode for development)
4. Select a location (choose closest to your users)
5. Click "Enable"

## Step 3: Enable Firebase Storage

1. In Firebase Console, go to **Build** > **Storage**
2. Click "Get started"
3. Start in **Production mode**
4. Use the default bucket location or choose your own
5. Click "Done"

## Step 4: Get Service Account Key

1. In Firebase Console, click the gear icon ⚙️ next to "Project Overview"
2. Select **Project Settings**
3. Go to **Service Accounts** tab
4. Click **Generate new private key**
5. A JSON file will download - **save this file securely!**
6. Note the file path (e.g., `/Users/yourname/Downloads/ethera-jewelry-firebase-adminsdk-xxxxx.json`)

## Step 5: Get Storage Bucket Name

1. In Firebase Console, go to **Build** > **Storage**
2. Look at the top of the page - you'll see your bucket name
3. Format: `your-project-id.appspot.com`
4. Example: `ethera-jewelry-12345.appspot.com`

## Step 6: Set Environment Variables

### Option A: Using .env file (Recommended for Local Development)

1. Create a `.env` file in the project root:

```bash
touch .env
```

2. Add these lines to `.env`:

```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/firebase-service-account-key.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

**Example `.env` file:**
```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/kaanyarali/Downloads/ethera-jewelry-firebase-adminsdk-xxxxx.json
FIREBASE_STORAGE_BUCKET=ethera-jewelry-12345.appspot.com
```

**Important:**
- Use the **absolute path** to your service account JSON file
- Replace `your-project-id.appspot.com` with your actual bucket name
- **Never commit `.env` to git** (it's already in `.gitignore`)

### Option B: Using Shell Environment Variables

**On macOS/Linux:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/firebase-service-account-key.json"
export FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
```

**On Windows (PowerShell):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\firebase-service-account-key.json"
$env:FIREBASE_STORAGE_BUCKET="your-project-id.appspot.com"
```

**On Windows (Command Prompt):**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\firebase-service-account-key.json
set FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

### Option C: For Cloud Run Deployment

**Important:** When deploying to Cloud Run, you do NOT need `GOOGLE_APPLICATION_CREDENTIALS` because Cloud Run automatically provides default credentials through the service account.

You only need to set `FIREBASE_STORAGE_BUCKET` as an environment variable in Cloud Run:

1. Go to Cloud Run Console > Your Service > Edit & Deploy New Revision
2. Go to "Variables & Secrets" tab
3. Add: `FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com`

Or via gcloud CLI:
```bash
gcloud run services update your-service-name \
  --region us-central1 \
  --set-env-vars FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

See `CLOUD_RUN_DEPLOYMENT.md` for complete Cloud Run deployment instructions.

## Step 7: Verify Setup

1. Make sure your service account JSON file exists at the path you specified
2. Check that Firestore and Storage are enabled in Firebase Console
3. Run the application:

```bash
uvicorn app.main:app --reload
```

4. If you see no errors, the setup is successful!

## Troubleshooting

### Error: "Could not initialize Firebase Admin SDK"
- Check that `GOOGLE_APPLICATION_CREDENTIALS` points to a valid JSON file
- Verify the JSON file is a valid service account key
- Make sure the path is absolute (not relative)

### Error: "Could not initialize Firebase Storage bucket"
- Check that `FIREBASE_STORAGE_BUCKET` is set correctly
- Verify the bucket name matches exactly (including `.appspot.com`)
- Make sure Storage is enabled in Firebase Console

### Error: "Permission denied"
- Make sure your service account has the right permissions:
  - **Firestore**: Cloud Datastore User
  - **Storage**: Storage Admin (or Storage Object Admin)

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your service account JSON file to git
- Never share your service account key publicly
- The `.env` file is already in `.gitignore` - don't remove it
- For production, use Cloud Run's default credentials instead of service account files

## Next Steps

Once setup is complete:
1. The app will automatically connect to Firestore
2. Product images will be uploaded to Firebase Storage (if `FIREBASE_STORAGE_BUCKET` is set)
3. All data will be stored in your Firebase project
