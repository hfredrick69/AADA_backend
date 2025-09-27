import os
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User, Document
from auth_utils import get_current_active_user
from services.storage_service import storage_service

router = APIRouter(tags=["Documents"])

# Pydantic models
class DocumentResponse(BaseModel):
    id: int
    document_type: str
    file_name: str
    file_url: str
    file_size: int
    verification_status: str
    verification_notes: Optional[str] = None
    uploaded_at: str
    verified_at: Optional[str] = None

class DocumentVerificationRequest(BaseModel):
    verification_status: str  # approved, rejected
    verification_notes: str = None

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_DOCUMENT_TYPES = ["id", "diploma", "certificate", "transcript", "other"]
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check file size
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Check file extension
    if file.filename:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Allowed types: {list(ALLOWED_EXTENSIONS)}"
            )

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a document for the current user."""

    # Validate inputs
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type. Allowed types: {ALLOWED_DOCUMENT_TYPES}"
        )

    validate_file(file)

    if not storage_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service not available. Please configure Azure Storage."
        )

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Reset file pointer and upload to Azure
        import io
        file_stream = io.BytesIO(file_content)

        blob_name, blob_url = storage_service.upload_document(
            user_id=current_user.id,
            document_type=document_type,
            file_content=file_stream,
            filename=file.filename
        )

        # Save document record to database
        document = Document(
            user_id=current_user.id,
            document_type=document_type,
            file_name=file.filename,
            file_url=blob_url,
            file_size=file_size,
            verification_status="pending"
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return DocumentResponse(
            id=document.id,
            document_type=document.document_type,
            file_name=document.file_name,
            file_url=document.file_url,
            file_size=document.file_size,
            verification_status=document.verification_status,
            verification_notes=document.verification_notes,
            uploaded_at=document.uploaded_at.isoformat(),
            verified_at=document.verified_at.isoformat() if document.verified_at else None
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("/list", response_model=List[DocumentResponse])
def list_user_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all documents for the current user."""
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()

    return [
        DocumentResponse(
            id=doc.id,
            document_type=doc.document_type,
            file_name=doc.file_name,
            file_url=doc.file_url,
            file_size=doc.file_size,
            verification_status=doc.verification_status,
            verification_notes=doc.verification_notes,
            uploaded_at=doc.uploaded_at.isoformat(),
            verified_at=doc.verified_at.isoformat() if doc.verified_at else None
        )
        for doc in documents
    ]

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return DocumentResponse(
        id=document.id,
        document_type=document.document_type,
        file_name=document.file_name,
        file_url=document.file_url,
        file_size=document.file_size,
        verification_status=document.verification_status,
        verification_notes=document.verification_notes,
        uploaded_at=document.uploaded_at.isoformat(),
        verified_at=document.verified_at.isoformat() if document.verified_at else None
    )

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a temporary download URL for a document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not storage_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service not available"
        )

    try:
        # Extract blob name from URL
        blob_name = document.file_url.split("/")[-1]
        download_url = storage_service.generate_download_url(blob_name)

        # Redirect to the download URL
        return RedirectResponse(url=download_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    try:
        # Delete from Azure Storage
        if storage_service:
            # Extract blob name from URL
            blob_name = document.file_url.split("/")[-1]
            storage_service.delete_document(blob_name)

        # Delete from database
        db.delete(document)
        db.commit()

        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

# Admin endpoints for document verification
@router.put("/{document_id}/verify")
def verify_document(
    document_id: int,
    verification: DocumentVerificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a document (admin only)."""
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can verify documents"
        )

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update verification status
    document.verification_status = verification.verification_status
    document.verification_notes = verification.verification_notes
    document.verified_by = current_user.id
    document.verified_at = datetime.utcnow()

    db.commit()

    return {"message": f"Document {verification.verification_status} successfully"}

@router.get("/admin/pending", response_model=List[DocumentResponse])
def list_pending_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all pending documents (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view pending documents"
        )

    documents = db.query(Document).filter(Document.verification_status == "pending").all()

    return [
        DocumentResponse(
            id=doc.id,
            document_type=doc.document_type,
            file_name=doc.file_name,
            file_url=doc.file_url,
            file_size=doc.file_size,
            verification_status=doc.verification_status,
            verification_notes=doc.verification_notes,
            uploaded_at=doc.uploaded_at.isoformat(),
            verified_at=doc.verified_at.isoformat() if doc.verified_at else None
        )
        for doc in documents
    ]