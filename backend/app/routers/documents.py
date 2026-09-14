import os
import uuid
from io import BytesIO
import json

import pika
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User, ProcessingJob, VerificationResult
from app.rabbitmq import RABBITMQ_QUEUE, get_rabbitmq_connection
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
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type",
        )

    # Read file
    file_content = file.file.read()

    # Validate file size
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
        # Upload file to MinIO
        minio_client.put_object(
            MINIO_BUCKET_NAME,
            object_name,
            BytesIO(file_content),
            length=len(file_content),
            content_type=file.content_type,
        )

        # Create document record
        document = Document(
            user_id=current_user.id,
            original_filename=file.filename,
            object_name=object_name,
            content_type=file.content_type,
            file_size=len(file_content),
            status="UPLOADED",
        )

        db.add(document)

        # Get document ID before commit
        db.flush()

        # Create processing job
        job = ProcessingJob(
            document_id=document.id,
            status="QUEUED",
        )

        db.add(job)

        # Save document + job to PostgreSQL
        db.commit()

        db.refresh(document)
        db.refresh(job)

        # Publish processing job to RabbitMQ
        connection = None

        try:
            connection = get_rabbitmq_connection()

            channel = connection.channel()

            channel.queue_declare(
                queue=RABBITMQ_QUEUE,
                durable=True,
            )

            message = str(job.id)

            channel.basic_publish(
                exchange="",
                routing_key=RABBITMQ_QUEUE,
                body=message.encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )

        finally:
            if connection is not None:
                connection.close()

        return {
            "id": document.id,
            "original_filename": document.original_filename,
            "content_type": document.content_type,
            "file_size": document.file_size,
            "status": document.status,
            "job_id": job.id,
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
@router.get("/{document_id}/result")
def get_document_result(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this document",
        )

    result = (
        db.query(VerificationResult)
        .filter(
            VerificationResult.document_id == document_id
        )
        .first()
    )

    if not result:
        return {
            "document_id": document_id,
            "status": document.status,
            "result": None,
        }

    return {
        "document_id": document_id,
        "status": document.status,
        "result": {
            "document_type": result.document_type,
            "extracted_name": result.extracted_name,
            "extracted_document_number": (
                result.extracted_document_number
            ),
            "confidence": result.confidence,
            "risk_level": result.risk_level,
            "risk_reasons": json.loads(
                result.risk_reasons
            )
            if result.risk_reasons
            else [],
            "verification_status": (
                result.verification_status
            ),
        },
    }