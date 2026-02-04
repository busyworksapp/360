"""
S3-Compatible Storage Service
Handles file uploads to Railway Object Storage (S3-compatible)
"""
import os
from dotenv import load_dotenv
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import secrets
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class S3StorageService:
    """S3-compatible storage service for file uploads"""
    
    def __init__(self):
        """Initialize S3 client with Railway Object Storage credentials"""
        self.endpoint_url = os.getenv('S3_ENDPOINT_URL')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.access_key = os.getenv('S3_ACCESS_KEY_ID')
        self.secret_key = os.getenv('S3_SECRET_ACCESS_KEY')
        self.region = os.getenv('S3_REGION', 'auto')
        
        # Initialize S3 client
        if self.endpoint_url and self.bucket_name:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                config=Config(
                    signature_version='s3v4',
                    s3={'addressing_style': 'virtual'}
                )
            )
            self.enabled = True
            print(f"✅ S3 Storage initialized: {self.bucket_name}")
        else:
            self.s3_client = None
            self.enabled = False
            print("⚠️ S3 Storage disabled - using local storage")
    
    def upload_file(self, file, folder='uploads', allowed_extensions=None):
        """
        Upload a file to S3 storage
        
        Args:
            file: FileStorage object from Flask request
            folder: Folder path in bucket (e.g., 'products', 'proofs')
            allowed_extensions: Set of allowed file extensions
            
        Returns:
            tuple: (file_url, error_message)
        """
        if not self.enabled:
            return None, "S3 storage not configured"
        
        # Validate file
        if not file:
            return None, "No file provided"
        
        # Check file size (16MB limit)
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        
        if size > 16 * 1024 * 1024:  # 16MB
            return None, "File too large (max 16MB)"
        
        if size == 0:
            return None, "File is empty"
        
        # Sanitize and validate filename
        filename = secure_filename(file.filename)
        if not filename:
            return None, "Invalid filename"
        
        # Check extension
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if allowed_extensions and ext not in allowed_extensions:
            return None, f"File type .{ext} not allowed"
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_id = secrets.token_hex(8)
        unique_filename = f"{timestamp}_{random_id}.{ext}"
        
        # Full S3 key (path)
        s3_key = f"{folder}/{unique_filename}"
        
        try:
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type or 'application/octet-stream',
                    'ACL': 'public-read'  # Make publicly accessible
                }
            )
            
            # Generate public URL
            file_url = f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"
            
            print(f"✅ File uploaded: {s3_key}")
            return file_url, None
            
        except ClientError as e:
            error_msg = f"S3 upload failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    def delete_file(self, file_url):
        """
        Delete a file from S3 storage
        
        Args:
            file_url: Full URL of the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Extract S3 key from URL
            # URL format: https://t3.storageapi.dev/bucket-name/folder/file.ext
            s3_key = file_url.split(f"{self.bucket_name}/")[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            print(f"✅ File deleted: {s3_key}")
            return True
            
        except Exception as e:
            print(f"❌ Delete failed: {str(e)}")
            return False
    
    def generate_presigned_url(self, s3_key, expiration=3600):
        """
        Generate a presigned URL for temporary access to a private file
        
        Args:
            s3_key: S3 object key (path in bucket)
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            str: Presigned URL or None
        """
        if not self.enabled:
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"❌ Presigned URL generation failed: {str(e)}")
            return None
    
    def list_files(self, folder=''):
        """
        List all files in a folder
        
        Args:
            folder: Folder path to list
            
        Returns:
            list: List of file keys
        """
        if not self.enabled:
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=folder
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except Exception as e:
            print(f"❌ List files failed: {str(e)}")
            return []
    
    def get_file_url(self, s3_key):
        """
        Get public URL for a file
        
        Args:
            s3_key: S3 object key
            
        Returns:
            str: Public URL
        """
        if not self.enabled:
            return None
        
        return f"{self.endpoint_url}/{self.bucket_name}/{s3_key}"


# Global instance
storage_service = S3StorageService()


# Helper functions for easy use
def upload_product_image(file):
    """Upload a product image"""
    allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return storage_service.upload_file(file, folder='products', allowed_extensions=allowed)


def upload_proof_of_payment(file):
    """Upload a proof of payment document"""
    allowed = {'png', 'jpg', 'jpeg', 'pdf'}
    return storage_service.upload_file(file, folder='proofs', allowed_extensions=allowed)


def upload_invoice_file(file):
    """Upload an invoice document"""
    allowed = {'pdf', 'png', 'jpg', 'jpeg'}
    return storage_service.upload_file(file, folder='invoices', allowed_extensions=allowed)


def delete_file(file_url):
    """Delete a file from storage"""
    return storage_service.delete_file(file_url)
