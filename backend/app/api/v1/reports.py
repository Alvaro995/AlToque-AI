"""Endpoints para generación y descarga de reportes clínicos longitudinales (F-12)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.reporting import MedicalReport
from app.schemas.reporting import ReportGenerateRequest, MedicalReportResponse
from app.services.report_service import ReportService
from app.services.pdf_generator_service import PDFGeneratorService

router = APIRouter(prefix="/reports", tags=["Reportes"])
report_service = ReportService()


@router.post("/generate", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_medical_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genera reporte clínico longitudinal con métricas de adherencia y hábitos."""
    report = await report_service.create_medical_report(
        db=db,
        user_id=current_user.id,
        start_date=req.period_start,
        end_date=req.period_end,
    )
    return report


@router.get("/", response_model=List[MedicalReportResponse])
async def list_medical_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista el historial de reportes generados para el paciente."""
    res = await db.execute(
        select(MedicalReport)
        .where(MedicalReport.user_id == current_user.id)
        .order_by(MedicalReport.generated_at.desc())
    )
    return list(res.scalars().all())


@router.get("/{report_id}/pdf")
async def download_report_pdf(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Genera y descarga el archivo PDF del reporte clínico para el médico."""
    res = await db.execute(
        select(MedicalReport).where(
            MedicalReport.id == report_id,
            MedicalReport.user_id == current_user.id,
        )
    )
    report = res.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")

    report_data = await report_service.generate_report_data(
        db=db,
        user_id=current_user.id,
        start_date=report.period_start,
        end_date=report.period_end,
    )
    pdf_bytes = PDFGeneratorService.generate_clinical_summary_pdf(report_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_clinico_{report.period_start}_{report.period_end}.pdf"
        },
    )
