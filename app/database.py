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

# Get Firestore client - use specified database ID or default to "(default)"
database_id = os.getenv("FIRESTORE_DATABASE_ID", "(default)")
db = None
try:
    db = firestore.client(database=database_id)
    print(f"✓ Firestore client initialized (database: {database_id})")
except Exception as e:
    print(f"⚠ Firestore client initialization error: {e}")
    print("⚠ Attempting to initialize without database ID...")
    try:
        db = firestore.client()
        print("✓ Firestore client initialized with default database")
    except Exception as e2:
        print(f"⚠⚠⚠ CRITICAL: Firestore client initialization failed: {e2}")
        print("⚠⚠⚠ App will start but database operations will fail!")
        print("⚠⚠⚠ Check your GCP_PROJECT_ID and FIRESTORE_DATABASE_ID environment variables")
        # Don't raise - let app start so we can see the error in logs

def get_db() -> Generator:
    """Firestore client dependency (replaces SQLAlchemy session)"""
    if db is None:
        raise HTTPException(
            status_code=503, 
            detail="Database not initialized. Check Cloud Run logs for Firebase initialization errors."
        )
    yield db
