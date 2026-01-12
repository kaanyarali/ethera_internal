import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Generator
from dotenv import load_dotenv

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
db = firestore.client(database=database_id)

def get_db() -> Generator:
    """Firestore client dependency (replaces SQLAlchemy session)"""
    yield db
