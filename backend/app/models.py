from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey , Integer, String
from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="USER"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    object_name: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="UPLOADED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="QUEUED"
    )

    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class VerificationResult(Base):
    __tablename__ = "verification_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        unique=True,
        index=True
    )

    document_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    extracted_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    extracted_document_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    confidence: Mapped[float | None] = mapped_column(
        nullable=True
    )

    risk_level: Mapped[str | None] = mapped_column(
    String(20),
    nullable=True
    )

    risk_reasons: Mapped[str | None] = mapped_column(
    String(2000),
    nullable=True
    )

    verification_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )