"""Endpoints para ingesta y extracción de reportes clínicos y horarios (F-01, F-02)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.ingestion import UploadedDocument, ClinicalRecord, ScheduleBlock
from app.schemas.ingestion import (
    DocumentType,
    DocumentUploadResponse,
    DocumentStatusResponse,
    ClinicalRecordResponse,
    ScheduleBlockCreate,
    ScheduleBlockResponse,
)
from app.services.llm_extraction_service import LLMExtractionService

router = APIRouter(prefix="/ingestion", tags=["Ingesta"])
extraction_service = LLMExtractionService()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Carga un documento clínico o de cronograma para extracción estructurada."""
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo proporcionado está vacío",
        )

    # Persistencia de metadatos del documento
    doc = UploadedDocument(
        user_id=current_user.id,
        doc_type=doc_type.value,
        file_url=f"/uploads/{file.filename}",
        mime_type=file.content_type or "application/octet-stream",
        original_filename=file.filename or "uploaded_document",
        status="pending",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Procesamiento del pipeline de extracción
    await extraction_service.process_document_pipeline(
        db=db,
        document=doc,
        file_bytes=file_bytes,
    )
    await db.refresh(doc)

    return doc


@router.get("/documents", response_model=List[DocumentStatusResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los documentos cargados del usuario y su estado de procesamiento."""
    res = await db.execute(
        select(UploadedDocument)
        .where(UploadedDocument.user_id == current_user.id)
        .order_by(UploadedDocument.uploaded_at.desc())
    )
    return list(res.scalars().all())


@router.get("/documents/{document_id}", response_model=DocumentStatusResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el detalle y estado de procesamiento de un documento específico."""
    res = await db.execute(
        select(UploadedDocument).where(
            UploadedDocument.id == document_id,
            UploadedDocument.user_id == current_user.id,
        )
    )
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    return doc


@router.get("/clinical-records", response_model=List[ClinicalRecordResponse])
async def list_clinical_records(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los parámetros clínicos de laboratorio extraídos para el usuario."""
    res = await db.execute(
        select(ClinicalRecord)
        .where(ClinicalRecord.user_id == current_user.id)
        .options(selectinload(ClinicalRecord.parameters))
        .order_by(ClinicalRecord.created_at.desc())
    )
    return list(res.scalars().all())


@router.get("/schedule-blocks", response_model=List[ScheduleBlockResponse])
async def list_schedule_blocks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista los bloques de horario y rutinas fijas del usuario."""
    res = await db.execute(
        select(ScheduleBlock)
        .where(ScheduleBlock.user_id == current_user.id)
        .order_by(ScheduleBlock.day_of_week, ScheduleBlock.start_time)
    )
    return list(res.scalars().all())


@router.post("/schedule-blocks", response_model=ScheduleBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule_block(
    block_in: ScheduleBlockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra manualmente un bloque de horario en la rutina."""
    block = ScheduleBlock(
        user_id=current_user.id,
        day_of_week=block_in.day_of_week,
        start_time=block_in.start_time,
        end_time=block_in.end_time,
        block_type=block_in.block_type.value,
        label=block_in.label,
    )
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block
