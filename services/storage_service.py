import os
import uuid
from datetime import datetime
from typing import BinaryIO, Tuple, Optional
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError
import mimetypes

class AzureStorageService:
    def __init__(self):
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "aada-documents")

        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set")

        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            # Create container if it doesn't exist
            self._ensure_container_exists()
        except Exception as e:
            print(f"Failed to initialize Azure Blob Storage: {e}")
            raise

    def _ensure_container_exists(self):
        """Create the container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.create_container()
        except AzureError as e:
            # Container might already exist
            if "ContainerAlreadyExists" not in str(e):
                print(f"Warning: Could not create container: {e}")

    def _generate_blob_name(self, user_id: int, document_type: str, original_filename: str) -> str:
        """Generate a unique blob name for the document."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(original_filename)[1].lower()
        unique_id = str(uuid.uuid4())[:8]

        # Format: user_123/id/20240327_143022_abc12def.jpg
        blob_name = f"user_{user_id}/{document_type}/{timestamp}_{unique_id}{file_extension}"
        return blob_name

    def _get_content_type(self, filename: str) -> str:
        """Get the content type based on file extension."""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or "application/octet-stream"

    def upload_document(
        self,
        user_id: int,
        document_type: str,
        file_content: BinaryIO,
        filename: str
    ) -> Tuple[str, str]:
        """
        Upload a document to Azure Blob Storage.

        Args:
            user_id: The ID of the user uploading the document
            document_type: Type of document (id, diploma, certificate, etc.)
            file_content: The file content as bytes
            filename: Original filename

        Returns:
            Tuple of (blob_name, blob_url)
        """
        try:
            # Validate file type
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
            file_extension = os.path.splitext(filename)[1].lower()

            if file_extension not in allowed_extensions:
                raise ValueError(f"File type {file_extension} not allowed. Allowed types: {allowed_extensions}")

            # Generate unique blob name
            blob_name = self._generate_blob_name(user_id, document_type, filename)

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Get content type
            content_type = self._get_content_type(filename)

            # Upload the file
            blob_client.upload_blob(
                file_content,
                overwrite=True,
                content_settings={'content_type': content_type}
            )

            # Get the blob URL
            blob_url = blob_client.url

            print(f"Successfully uploaded document: {blob_name}")
            return blob_name, blob_url

        except Exception as e:
            print(f"Error uploading document: {e}")
            raise

    def delete_document(self, blob_name: str) -> bool:
        """
        Delete a document from Azure Blob Storage.

        Args:
            blob_name: The name of the blob to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            print(f"Successfully deleted document: {blob_name}")
            return True
        except Exception as e:
            print(f"Error deleting document {blob_name}: {e}")
            return False

    def get_document_url(self, blob_name: str) -> str:
        """
        Get the URL for a document.

        Args:
            blob_name: The name of the blob

        Returns:
            The URL of the document
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        return blob_client.url

    def generate_download_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Generate a temporary download URL with SAS token.

        Args:
            blob_name: The name of the blob
            expiry_hours: How many hours the URL should be valid

        Returns:
            A temporary URL with SAS token
        """
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import timedelta

            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )

            # Get blob URL with SAS token
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return f"{blob_client.url}?{sas_token}"

        except Exception as e:
            print(f"Error generating download URL: {e}")
            # Return the regular URL as fallback
            return self.get_document_url(blob_name)

    def list_user_documents(self, user_id: int) -> list:
        """
        List all documents for a specific user.

        Args:
            user_id: The ID of the user

        Returns:
            List of blob names for the user
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs(name_starts_with=f"user_{user_id}/")
            return [blob.name for blob in blob_list]
        except Exception as e:
            print(f"Error listing documents for user {user_id}: {e}")
            return []

# Global instance - use mock service for testing if Azure is not configured
try:
    if os.getenv("AZURE_STORAGE_CONNECTION_STRING") and "PLACEHOLDER_KEY" not in os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""):
        storage_service = AzureStorageService()
        print("✅ Using Azure Blob Storage")
    else:
        from .mock_storage_service import mock_storage_service
        storage_service = mock_storage_service
        print("🧪 Using Mock Storage Service for testing")
except Exception as e:
    print(f"⚠️  Storage service initialization failed: {e}")
    from .mock_storage_service import mock_storage_service
    storage_service = mock_storage_service
    print("🧪 Falling back to Mock Storage Service")