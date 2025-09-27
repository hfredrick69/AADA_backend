import os
import uuid
from datetime import datetime
from typing import BinaryIO, Tuple, Optional
import mimetypes

class MockStorageService:
    """Mock storage service for testing without Azure Storage account."""

    def __init__(self):
        self.container_name = "aada-documents"
        # Use local temp directory for storing files during testing
        self.base_path = "/tmp/aada_documents"
        os.makedirs(self.base_path, exist_ok=True)
        print(f"📁 Mock Storage initialized at: {self.base_path}")

    def _generate_blob_name(self, user_id: int, document_type: str, original_filename: str) -> str:
        """Generate a unique blob name for the document."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(original_filename)[1].lower()
        unique_id = str(uuid.uuid4())[:8]

        # Format: user_123/id/20240327_143022_abc12def.jpg
        blob_name = f"user_{user_id}/{document_type}/{timestamp}_{unique_id}{file_extension}"
        return blob_name

    def upload_document(
        self,
        user_id: int,
        document_type: str,
        file_content: BinaryIO,
        filename: str
    ) -> Tuple[str, str]:
        """
        Upload a document to mock storage.
        """
        try:
            # Validate file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
            file_extension = os.path.splitext(filename)[1].lower()

            if file_extension not in allowed_extensions:
                raise ValueError(f"File type {file_extension} not allowed. Allowed types: {allowed_extensions}")

            # Generate unique blob name
            blob_name = self._generate_blob_name(user_id, document_type, filename)

            # Create directory structure
            file_path = os.path.join(self.base_path, blob_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save file to local storage
            with open(file_path, 'wb') as f:
                content = file_content.read()
                f.write(content)

            # Generate mock URL
            blob_url = f"http://localhost:8000/mock-storage/{blob_name}"

            print(f"📄 Mock file saved: {blob_name}")
            return blob_name, blob_url

        except Exception as e:
            print(f"❌ Error uploading document: {e}")
            raise

    def delete_document(self, blob_name: str) -> bool:
        """Delete a document from mock storage."""
        try:
            file_path = os.path.join(self.base_path, blob_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️  Mock file deleted: {blob_name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting document {blob_name}: {e}")
            return False

    def get_document_url(self, blob_name: str) -> str:
        """Get the URL for a document."""
        return f"http://localhost:8000/mock-storage/{blob_name}"

    def generate_download_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """Generate a temporary download URL."""
        # For mock, just return the regular URL
        return self.get_document_url(blob_name)

    def list_user_documents(self, user_id: int) -> list:
        """List all documents for a specific user."""
        try:
            user_dir = os.path.join(self.base_path, f"user_{user_id}")
            if not os.path.exists(user_dir):
                return []

            blob_names = []
            for root, dirs, files in os.walk(user_dir):
                for file in files:
                    # Get relative path from base_path
                    full_path = os.path.join(root, file)
                    blob_name = os.path.relpath(full_path, self.base_path)
                    blob_names.append(blob_name)

            return blob_names
        except Exception as e:
            print(f"❌ Error listing documents for user {user_id}: {e}")
            return []

# Create mock service instance
mock_storage_service = MockStorageService()