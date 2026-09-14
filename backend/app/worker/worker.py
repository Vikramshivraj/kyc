import json
import time
from io import BytesIO

import pika
import pytesseract
from PIL import Image
from sqlalchemy.orm import Session

from app.processing.ocr import extract_text_from_file
from app.database import SessionLocal
from app.models import (
    Document,
    ProcessingJob,
    VerificationResult,
)
from app.storage import (
    MINIO_BUCKET_NAME,
    minio_client,
)
from app.rabbitmq import (
    RABBITMQ_QUEUE,
    get_rabbitmq_connection,
)
from app.processing.extractor import (
    extract_fields,
    identify_document_type,
)
from app.processing.validator import validate_fields
from app.processing.risk import (
    calculate_confidence,
    calculate_risk,
)


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def process_job(job_id: int, db: Session):
    job = db.get(ProcessingJob, job_id)

    if not job:
        print(f"Job {job_id} not found")
        return

    document = db.get(Document, job.document_id)

    if not document:
        raise ValueError(
            f"Document {job.document_id} not found"
        )

    print(f"Processing job {job_id}")

    job.status = "PROCESSING"
    document.status = "PROCESSING"
    db.commit()

    # Prevent duplicate verification results
    existing_result = (
        db.query(VerificationResult)
        .filter(
            VerificationResult.document_id == document.id
        )
        .first()
    )

    if existing_result:
        print(
            f"Verification result already exists "
            f"for document {document.id}"
        )

        job.status = "COMPLETED"
        document.status = "PROCESSED"
        db.commit()

        return

    try:
        response = minio_client.get_object(
            MINIO_BUCKET_NAME,
            document.object_name,
        )

        file_data = response.read()

        response.close()
        response.release_conn()

        ocr_text = extract_text_from_file(
            file_data,
            document.content_type,
        )

        print("OCR completed")
        print(ocr_text)

        document_type = identify_document_type(
            ocr_text
        )

        fields = extract_fields(ocr_text)

        print("EXTRACTED FIELDS:")
        print(fields)

        validation = validate_fields(fields)

        confidence = calculate_confidence(
            fields,
            validation,
        )

        risk = calculate_risk(
            confidence,
            validation,
        )

        result = VerificationResult(
            document_id=document.id,
            document_type=document_type,
            extracted_name=fields.get("name"),
            extracted_document_number=fields.get(
                "document_number"
            ),
            confidence=confidence,
            risk_level=risk["risk_level"],
            risk_reasons=json.dumps(
                risk["reasons"]
            ),
            verification_status="COMPLETED",
        )

        db.add(result)

        job.status = "COMPLETED"
        document.status = "PROCESSED"

        db.commit()

        print(
            f"Job {job_id} completed "
            f"with risk={risk['risk_level']}"
        )

    except Exception as error:
        db.rollback()

        job = db.get(ProcessingJob, job_id)

        if job:
            job.status = "FAILED"
            job.error_message = str(error)
            db.commit()

        raise


def callback(ch, method, properties, body):
    job_id = int(body.decode())

    print(f"Received job: {job_id}")

    db = SessionLocal()

    try:
        process_job(job_id, db)

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as error:
        print(
            f"Job {job_id} failed: {error}"
        )

        db.rollback()

        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )

    finally:
        db.close()


def start_worker():
    connection = get_rabbitmq_connection()

    channel = connection.channel()

    channel.queue_declare(
        queue=RABBITMQ_QUEUE,
        durable=True,
    )

    channel.basic_qos(
        prefetch_count=1
    )

    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=callback,
    )

    print("KYC Worker started...")
    print(
        f"Waiting for jobs from: {RABBITMQ_QUEUE}"
    )

    channel.start_consuming()


if __name__ == "__main__":
    start_worker()