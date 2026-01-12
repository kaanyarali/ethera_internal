import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Generator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    # For local development: use service account key
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
    else:
        # For Cloud Run: uses default credentials
        try:
            firebase_admin.initialize_app()
        except ValueError:
            # Already initialized
            pass

# Get Firestore client
db = firestore.client()

def get_db() -> Generator:
    """Firestore client dependency (replaces SQLAlchemy session)"""
    yield db
