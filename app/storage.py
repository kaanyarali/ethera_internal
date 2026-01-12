import os
from firebase_admin import storage
from typing import Optional
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FirebaseStorage:
    def __init__(self):
        self.bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
        if self.bucket_name:
            try:
                self.bucket = storage.bucket(self.bucket_name)
            except Exception as e:
                print(f"Warning: Could not initialize Firebase Storage bucket: {e}")
                self.bucket = None
        else:
            self.bucket = None
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
        """Upload file to Firebase Storage and return public URL"""
        if not self.bucket:
            return None
        
        try:
            # Generate unique filename
            unique_filename = f"product_images/{uuid.uuid4()}_{filename}"
            blob = self.bucket.blob(unique_filename)
            
            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()  # Make publicly accessible
            
            return blob.public_url
        except Exception as e:
            print(f"Error uploading to Firebase Storage: {e}")
            return None
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from Firebase Storage by URL"""
        if not self.bucket:
            return False
        
        try:
            # Extract blob name from URL
            if self.bucket_name and self.bucket_name in file_url:
                blob_name = file_url.split(f"{self.bucket_name}/")[-1].split("?")[0]
                blob = self.bucket.blob(blob_name)
                blob.delete()
                return True
            # Try to extract from gs:// URL or other formats
            elif "gs://" in file_url:
                blob_name = file_url.split("gs://")[-1].split("/", 1)[-1]
                blob = self.bucket.blob(blob_name)
                blob.delete()
                return True
        except Exception as e:
            print(f"Error deleting from Firebase Storage: {e}")
            return False

storage_client = FirebaseStorage()
