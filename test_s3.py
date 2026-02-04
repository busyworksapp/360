"""
Test S3 Storage Connection
Quick test to verify Railway Object Storage is working
"""
from s3_storage import storage_service
from io import BytesIO

def test_s3_connection():
    """Test S3 connection and upload"""
    print("=" * 60)
    print("🧪 Testing S3 Storage Connection")
    print("=" * 60)
    
    # Check if S3 is enabled
    if not storage_service.enabled:
        print("❌ S3 storage is not enabled")
        print("   Check your .env file for S3 credentials")
        return False
    
    print(f"✅ S3 Client initialized")
    print(f"   Endpoint: {storage_service.endpoint_url}")
    print(f"   Bucket: {storage_service.bucket_name}")
    print(f"   Region: {storage_service.region}")
    
    # Test upload with a dummy file
    print("\n📤 Testing file upload...")
    
    try:
        # Create a test file
        test_content = b"This is a test file from 360Degree Supply"
        test_file = BytesIO(test_content)
        test_file.filename = "test.txt"
        test_file.content_type = "text/plain"
        
        # Upload
        file_url, error = storage_service.upload_file(
            test_file, 
            folder='test',
            allowed_extensions={'txt'}
        )
        
        if error:
            print(f"❌ Upload failed: {error}")
            return False
        
        print(f"✅ Upload successful!")
        print(f"   URL: {file_url}")
        
        # Test delete
        print("\n🗑️ Testing file deletion...")
        if storage_service.delete_file(file_url):
            print("✅ Delete successful!")
        else:
            print("⚠️ Delete failed (file may still exist)")
        
        print("\n" + "=" * 60)
        print("✅ S3 STORAGE TEST PASSED")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ S3 STORAGE TEST FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    test_s3_connection()
