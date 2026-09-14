import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.storage import minio_client, MINIO_BUCKET_NAME


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

MAX_FILE_SIZE = 5 * 1024 * 1024

def ensure_bucket_exists():
    if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
        minio_client.make_bucket(MINIO_BUCKET_NAME)

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    if not file.filename:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
         )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported file type",
    )

    file_content = file.file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5 MB limit",
        )

    ensure_bucket_exists()

    extension = os.path.splitext(file.filename)[1].lower()

    object_name = (
        f"{current_user.id}/"
        f"{uuid.uuid4()}{extension}"
    )

    try:
        minio_client.put_object(
            MINIO_BUCKET_NAME,
            object_name,
            BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type,
        )

        document = Document(
            user_id=current_user.id,
            original_filename=file.filename,
            object_name=object_name,
            content_type=file.content_type,
            file_size=len(file_content),
            status="UPLOADED",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return {
            "id": document.id,
            "original_filename": document.original_filename,
            "content_type": document.content_type,
            "file_size": document.file_size,
            "status": document.status,
        }

    except Exception:
        db.rollback()

        try:
            minio_client.remove_object(
                MINIO_BUCKET_NAME,
                object_name,
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )
    
@router.get("/")
def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "original_filename": document.original_filename,
            "content_type": document.content_type,
            "file_size": document.file_size,
            "status": document.status,
            "created_at": document.created_at,
        }
        for document in documents
    ]