"""Orquestador de extracción estructurada con OCR y LLM validado por esquemas."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import UploadedDocument
from app.services.ocr_service import OCRService
from app.services.clinical_parser_service import ClinicalParserService
from app.services.schedule_parser_service import ScheduleParserService

logger = logging.getLogger(__name__)


class LLMExtractionService:
    """Orchestrator for automated document ingestion pipelines."""

    def __init__(self):
        self.ocr_service = OCRService()
        self.clinical_parser = ClinicalParserService()
        self.schedule_parser = ScheduleParserService()

    async def process_document_pipeline(
        self,
        db: AsyncSession,
        document: UploadedDocument,
        file_bytes: bytes,
    ) -> dict:
        """
        Execute full extraction pipeline:
        1. Extract OCR text according to mime-type.
        2. Dispatch text to appropriate domain parser.
        3. Return structured status and extraction summary.
        """
        document.status = "processing"
        await db.commit()

        # Step 1: Text extraction
        if "pdf" in document.mime_type.lower():
            ocr_result = await self.ocr_service.extract_text_from_pdf(file_bytes)
        else:
            ocr_result = await self.ocr_service.extract_text_from_image(file_bytes)

        if not ocr_result.get("success") or not ocr_result.get("text"):
            document.status = "failed"
            document.error_detail = ocr_result.get("error", "No text could be extracted.")
            await db.commit()
            return {"status": "failed", "detail": document.error_detail}

        raw_text = ocr_result["text"]

        # Step 2: Domain-specific extraction
        try:
            if document.doc_type == "clinical":
                record = await self.clinical_parser.parse_and_store_clinical_document(
                    db=db,
                    document=document,
                    raw_text=raw_text,
                )
                return {
                    "status": "success",
                    "doc_type": "clinical",
                    "record_id": record.id,
                    "lab_date": str(record.lab_date),
                }
            elif document.doc_type == "schedule":
                blocks = await self.schedule_parser.parse_and_store_schedule_document(
                    db=db,
                    document=document,
                    raw_text=raw_text,
                )
                return {
                    "status": "success",
                    "doc_type": "schedule",
                    "blocks_count": len(blocks),
                }
            else:
                document.status = "failed"
                document.error_detail = f"Unsupported document type: {document.doc_type}"
                await db.commit()
                return {"status": "failed", "detail": document.error_detail}
        except Exception as e:
            logger.error(f"Pipeline error for document {document.id}: {str(e)}")
            document.status = "failed"
            document.error_detail = str(e)
            await db.commit()
            return {"status": "failed", "detail": str(e)}
