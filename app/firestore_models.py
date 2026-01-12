from typing import Dict, Any, Optional
from datetime import datetime
from firebase_admin import firestore

def document_to_dict(doc) -> Optional[Dict[str, Any]]:
    """Convert Firestore document to dict with id"""
    if not doc.exists:
        return None
    data = doc.to_dict()
    if data is None:
        return None
    data["id"] = doc.id
    return data

def timestamp_to_datetime(timestamp) -> Optional[datetime]:
    """Convert Firestore timestamp to datetime"""
    if timestamp is None:
        return None
    if isinstance(timestamp, datetime):
        return timestamp
    # Firestore timestamp
    return timestamp

def datetime_to_timestamp(dt: Optional[datetime]):
    """Convert datetime to Firestore timestamp"""
    if dt is None:
        return firestore.SERVER_TIMESTAMP
    return dt
