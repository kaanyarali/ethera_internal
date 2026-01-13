import os
from firebase_admin import storage
from typing import Optional
import uuid
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FirebaseStorage:
    def __init__(self):
        self.bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
        self._bucket = None  # Lazy initialization
        self._initialized = False
    
    def _ensure_bucket(self):
        """Lazy initialization of bucket - only when needed"""
        if self._initialized:
            return self._bucket
        
        self._initialized = True
        
        if not self.bucket_name:
            print("⚠ FIREBASE_STORAGE_BUCKET not set - image uploads will be disabled")
            return None
        
        try:
            # Try to get the bucket - this will fail if bucket doesn't exist
            self._bucket = storage.bucket(self.bucket_name)
            # Test if bucket exists by trying to get its metadata
            try:
                self._bucket.reload()
                print(f"✓ Firebase Storage bucket initialized: {self.bucket_name}")
            except Exception as e:
                print(f"⚠ Warning: Firebase Storage bucket '{self.bucket_name}' does not exist or is not accessible")
                print(f"⚠ Error: {e}")
                print(f"⚠ To fix this:")
                print(f"⚠   1. Go to Firebase Console: https://console.firebase.google.com/")
                print(f"⚠   2. Select your project: project-2799141d-0677-4078-a07")
                print(f"⚠   3. Go to Build > Storage")
                print(f"⚠   4. If Storage is not enabled, click 'Get started' to enable it")
                print(f"⚠   5. The bucket name will be shown at the top")
                print(f"⚠   6. Update FIREBASE_STORAGE_BUCKET in your .env file with the correct bucket name")
                self._bucket = None
        except Exception as e:
            print(f"⚠ Warning: Could not initialize Firebase Storage bucket: {e}")
            print(f"⚠ Bucket name: {self.bucket_name}")
            print(f"⚠ Please verify the bucket exists in Firebase Console > Storage")
            self._bucket = None
        
        return self._bucket
    
    @property
    def bucket(self):
        """Get bucket with lazy initialization"""
        return self._ensure_bucket()
    
    def upload_file(self, file_content: bytes, filename: str, content_type: str = "image/jpeg", sku: Optional[str] = None) -> Optional[str]:
        """Upload file to Firebase Storage and return signed URL
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file
            sku: Product SKU to organize files in subfolder (optional)
        """
        bucket = self.bucket  # This will trigger lazy initialization
        if not bucket:
            return None
        
        try:
            # Generate unique filename - organize by SKU if provided
            if sku:
                # Sanitize SKU for use in path (remove special characters)
                safe_sku = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in sku)
                unique_filename = f"product_images/{safe_sku}/{uuid.uuid4()}_{filename}"
            else:
                unique_filename = f"product_images/{uuid.uuid4()}_{filename}"
            blob = bucket.blob(unique_filename)
            
            blob.upload_from_string(file_content, content_type=content_type)
            
            # Generate signed URL (valid for 10 years) - this works with uniform bucket-level access
            try:
                signed_url = blob.generate_signed_url(
                    expiration=timedelta(days=3650),  # 10 years
                    method='GET'
                )
                print(f"Debug: Generated signed URL (valid for 10 years)")
                return signed_url
            except Exception as e:
                print(f"Debug: Could not generate signed URL: {e}")
                # Fallback: Try Firebase Storage public URL format
                import urllib.parse
                encoded_path = urllib.parse.quote(unique_filename, safe='')
                public_url = f"https://firebasestorage.googleapis.com/v0/b/{self.bucket_name}/o/{encoded_path}?alt=media"
                print(f"Debug: Using Firebase Storage URL format: {public_url}")
                return public_url
        except Exception as e:
            print(f"Error uploading to Firebase Storage: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_signed_url(self, file_url: str) -> Optional[str]:
        """Convert a storage URL to a signed URL if needed
        
        Args:
            file_url: Existing file URL (can be direct URL or signed URL)
        
        Returns:
            Signed URL valid for 10 years, or original URL if conversion fails
        """
        # If URL already contains a signature (signed URL), return as-is
        if "Signature=" in file_url or "X-Goog-Signature" in file_url:
            return file_url
        
        bucket = self.bucket
        if not bucket:
            return file_url
        
        try:
            # Extract blob path from URL
            blob_name = None
            import urllib.parse
            
            # Check if it's a storage.googleapis.com URL
            if f"{self.bucket_name}/" in file_url:
                # Extract from storage.googleapis.com URL
                parts = file_url.split(f"{self.bucket_name}/")
                if len(parts) > 1:
                    blob_name = urllib.parse.unquote(parts[1].split("?")[0])  # Remove query params and decode
            # Check if it's a firebasestorage.googleapis.com URL
            elif "firebasestorage.googleapis.com" in file_url:
                # Extract from Firebase Storage URL format: /v0/b/BUCKET/o/PATH?alt=media
                if "/o/" in file_url:
                    parts = file_url.split("/o/")
                    if len(parts) > 1:
                        encoded_path = parts[1].split("?")[0]
                        blob_name = urllib.parse.unquote(encoded_path)
            # Check if it's a signed URL with the blob path in it
            elif "storage.googleapis.com" in file_url:
                # Try to extract from any storage.googleapis.com URL
                if "/" in file_url:
                    # Find the path after the bucket name
                    if self.bucket_name in file_url:
                        parts = file_url.split(self.bucket_name)
                        if len(parts) > 1:
                            path_part = parts[1].split("?")[0]
                            if path_part.startswith("/"):
                                blob_name = urllib.parse.unquote(path_part[1:])  # Remove leading /
            
            if blob_name:
                blob = bucket.blob(blob_name)
                signed_url = blob.generate_signed_url(
                    expiration=timedelta(days=3650),
                    method='GET'
                )
                print(f"Debug: Generated signed URL for: {blob_name[:50]}...")
                return signed_url
            else:
                print(f"Debug: Could not extract blob name from URL: {file_url[:80]}...")
        except Exception as e:
            print(f"Debug: Could not generate signed URL for {file_url[:80]}...: {e}")
            import traceback
            traceback.print_exc()
        
        return file_url  # Return original URL if conversion fails
    
    def delete_file(self, file_url: str) -> bool:
        """Delete file from Firebase Storage by URL"""
        bucket = self.bucket  # This will trigger lazy initialization
        if not bucket:
            return False
        
        try:
            # Extract blob name from URL
            if self.bucket_name and self.bucket_name in file_url:
                blob_name = file_url.split(f"{self.bucket_name}/")[-1].split("?")[0]
                blob = bucket.blob(blob_name)
                blob.delete()
                return True
            # Try to extract from gs:// URL or other formats
            elif "gs://" in file_url:
                blob_name = file_url.split("gs://")[-1].split("/", 1)[-1]
                blob = bucket.blob(blob_name)
                blob.delete()
                return True
        except Exception as e:
            print(f"Error deleting from Firebase Storage: {e}")
            return False

storage_client = FirebaseStorage()
