# Secrets & Environment Variables Guide

This guide shows exactly what secrets/environment variables to set and where to paste them.

## 🔐 What You Need

### For Local Development (.env file)

Create a `.env` file in your project root with:

```env
GOOGLE_APPLICATION_CREDENTIALS=/Users/kaanyarali/Downloads/your-project-firebase-adminsdk-xxxxx.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
GCP_PROJECT_ID=your-project-id
FIRESTORE_DATABASE_ID=(default)
```

**Replace with your actual values:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Full path to your downloaded Firebase service account JSON file
- `FIREBASE_STORAGE_BUCKET`: Your Firebase Storage bucket name (found in Firebase Console > Storage)
- `GCP_PROJECT_ID`: Your Google Cloud Project ID (e.g., `project-2799141d-0677-4078-a07`) - **Required if database not found**
- `FIRESTORE_DATABASE_ID`: Your Firestore database ID (usually `(default)` unless you created a custom one)

---

## ☁️ For Cloud Run Deployment

### Option 1: Cloud Console (UI)

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service name
3. Click **"Edit & Deploy New Revision"**
4. Scroll to **"Variables & Secrets"** tab
5. Click **"Add Variable"**
6. Add these environment variables:

   **Name:** `FIREBASE_STORAGE_BUCKET`  
   **Value:** `your-project-id.appspot.com` (your actual bucket name)
   
   **Name:** `GCP_PROJECT_ID` (if needed)  
   **Value:** `your-project-id` (e.g., `project-2799141d-0677-4078-a07`)
   
   **Name:** `FIRESTORE_DATABASE_ID` (if using custom database)  
   **Value:** `(default)` or your custom database ID

7. Click **"Deploy"**

**⚠️ Important:** Do NOT add `GOOGLE_APPLICATION_CREDENTIALS` - Cloud Run uses default credentials automatically!

### Option 2: gcloud CLI

```bash
gcloud run services update ethera-jewelry \
  --region us-central1 \
  --set-env-vars FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com,GCP_PROJECT_ID=your-project-id,FIRESTORE_DATABASE_ID=(default)
```

---

## 🔄 For GitHub Actions (CI/CD)

If you're setting up GitHub Actions for automatic deployment:

1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **"New repository secret"**

### Secret 1: Service Account Key (for deployment)

**Name:** `GCP_SA_KEY`  
**Value:** Paste the entire contents of your Firebase service account JSON file

**How to get it:**
- Open your downloaded `your-project-firebase-adminsdk-xxxxx.json` file
- Copy the entire JSON content (all of it, including `{` and `}`)
- Paste it as the secret value

### Secret 2: Firebase Storage Bucket

**Name:** `FIREBASE_STORAGE_BUCKET`  
**Value:** `your-project-id.appspot.com`

### Secret 3: GCP Project ID (if needed)

**Name:** `GCP_PROJECT_ID`  
**Value:** `your-gcp-project-id`

---

## 📋 Quick Reference Table

| Platform | GOOGLE_APPLICATION_CREDENTIALS | FIREBASE_STORAGE_BUCKET |
|----------|-------------------------------|------------------------|
| **Local Dev (.env)** | ✅ Required (file path) | ✅ Required |
| **Cloud Run** | ❌ Not needed | ✅ Required (env var) |
| **GitHub Actions** | ✅ Required (JSON content) | ✅ Required (secret) |

---

## 🎯 Step-by-Step: Getting Your Values

### 1. Get Firebase Storage Bucket Name

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Build** > **Storage**
4. Look at the top - you'll see: `gs://your-project-id.appspot.com`
5. Your bucket name is: `your-project-id.appspot.com`

### 2. Get Service Account Key (for local dev or GitHub Actions)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click the ⚙️ gear icon > **Project Settings**
3. Go to **Service Accounts** tab
4. Click **"Generate new private key"**
5. A JSON file downloads - this is your service account key

**For Local Dev:**
- Save the file somewhere (e.g., `~/Downloads/`)
- Use the full path in `.env`: `/Users/kaanyarali/Downloads/filename.json`

**For GitHub Actions:**
- Open the JSON file
- Copy the entire content (all of it)
- Paste as secret value

---

## ✅ Example Values

Here's what your values might look like:

**FIREBASE_STORAGE_BUCKET:**
```
ethera-jewelry-abc123.appspot.com
```

**GOOGLE_APPLICATION_CREDENTIALS (local dev path):**
```
/Users/kaanyarali/Downloads/ethera-jewelry-firebase-adminsdk-abc123-def456.json
```

**GOOGLE_APPLICATION_CREDENTIALS (GitHub Actions - JSON content):**
```json
{
  "type": "service_account",
  "project_id": "ethera-jewelry",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@ethera-jewelry.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## 🚨 Security Reminders

- ✅ `.env` file is already in `.gitignore` - won't be committed
- ✅ Service account JSON files are in `.gitignore` - won't be committed
- ❌ Never commit secrets to git
- ❌ Never share service account keys publicly
- ✅ Use GitHub Secrets for CI/CD
- ✅ Cloud Run uses default credentials (no keys needed)

---

## 🆘 Troubleshooting

**"Could not initialize Firebase Admin SDK"**
- Check that `GOOGLE_APPLICATION_CREDENTIALS` path is correct (local dev)
- Verify the JSON file exists at that path
- For Cloud Run, this shouldn't happen (uses default credentials)

**"The database (default) does not exist for project..."**
- **Solution 1:** Set `GCP_PROJECT_ID` environment variable to your project ID
  - Find your project ID in GCP Console or Firebase Console
  - Example: `GCP_PROJECT_ID=project-2799141d-0677-4078-a07`
- **Solution 2:** Verify the database exists in Firebase Console
  - Go to Firebase Console > Firestore Database
  - Make sure a database is created
  - Note the database ID (usually `(default)`)
- **Solution 3:** If using a custom database ID, set `FIRESTORE_DATABASE_ID`
  - Example: `FIRESTORE_DATABASE_ID=production`

**"Could not initialize Firebase Storage bucket"**
- Verify `FIREBASE_STORAGE_BUCKET` is set correctly
- Check bucket name format: `project-id.appspot.com`
- Ensure Storage is enabled in Firebase Console

### How to Find Your Project ID

1. **From Error Message:**
   - Look at the error: `project-2799141d-0677-4078-a07` is your project ID
   
2. **From GCP Console:**
   - Go to [GCP Console](https://console.cloud.google.com/)
   - Project ID is shown at the top
   
3. **From Firebase Console:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click Project Settings (gear icon)
   - Project ID is shown in "General" tab

### How to Find Your Database ID

1. Go to [Firebase Console](https://console.firebase.google.com/) > Firestore Database
2. If you see multiple databases, each has an ID
3. Default database ID is: `(default)`
4. Custom databases show their name (e.g., `production`, `staging`)
