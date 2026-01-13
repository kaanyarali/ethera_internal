import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Generator
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # Get project ID from environment or service account
        project_id = os.getenv("GCP_PROJECT_ID") or os.getenv("FIREBASE_PROJECT_ID")
        
        # For local development: use service account key
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            # If project_id is specified, use it in options
            if project_id:
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id
                })
            else:
                firebase_admin.initialize_app(cred)
        else:
            # For Cloud Run: uses default credentials
            if project_id:
                firebase_admin.initialize_app(options={'projectId': project_id})
            else:
                firebase_admin.initialize_app()
        print("✓ Firebase Admin SDK initialized successfully")
    except ValueError as e:
        # Already initialized
        if "already exists" not in str(e).lower():
            print(f"⚠ Firebase initialization warning: {e}")
    except Exception as e:
        print(f"⚠ Firebase initialization error: {e}")
        print("⚠ App will start but Firestore operations may fail")

# Get Firestore client
# Note: The 'database' parameter is not supported in google-cloud-firestore 2.14.0
# It will use the default database. For multi-database support, upgrade to a newer version.
database_id = os.getenv("FIRESTORE_DATABASE_ID", "(default)")
db = None
try:
    # Try to initialize Firestore client (without database parameter for compatibility)
    db = firestore.client()
    if database_id != "(default)":
        print(f"⚠ Note: Database ID '{database_id}' specified but not supported in this version")
        print(f"⚠ Using default database. Upgrade google-cloud-firestore for multi-database support.")
    print(f"✓ Firestore client initialized (using default database)")
except Exception as e:
    print(f"⚠⚠⚠ CRITICAL: Firestore client initialization failed: {e}")
    print("⚠⚠⚠ App will start but database operations will fail!")
    print("⚠⚠⚠ Check your GOOGLE_APPLICATION_CREDENTIALS and GCP_PROJECT_ID environment variables")
    import traceback
    traceback.print_exc()
    # Don't raise - let app start so we can see the error in logs

def get_db() -> Generator:
    """Firestore client dependency (replaces SQLAlchemy session)"""
    if db is None:
        error_detail = "Database not initialized. "
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            error_detail += f"Check that GOOGLE_APPLICATION_CREDENTIALS points to a valid file: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
        else:
            error_detail += "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. Check your .env file or environment variables."
        raise HTTPException(
            status_code=503, 
            detail=error_detail
        )
    yield db
