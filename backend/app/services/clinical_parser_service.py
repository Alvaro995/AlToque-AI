"""Servicio de validación de biomarcadores clínicos y cálculo de HOMA-IR."""

from datetime import datetime, date
import re
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingestion import UploadedDocument, ClinicalRecord, ClinicalParameter
from app.services.llm_service import LLMService


class ClinicalParserService:
    """Service to parse, validate, and persist clinical laboratory results."""

    def __init__(self):
        self.llm = LLMService()

    @staticmethod
    def calculate_homa_ir(glucose_mg_dl: float, insulin_uIU_ml: float) -> float:
        """
        Calculate Homeostatic Model Assessment for Insulin Resistance.
        Formula: HOMA-IR = (Glucose [mg/dL] * Insulin [uIU/mL]) / 405.0
        """
        if glucose_mg_dl <= 0 or insulin_uIU_ml <= 0:
            return 0.0
        return round((glucose_mg_dl * insulin_uIU_ml) / 405.0, 2)

    @staticmethod
    def assign_parameter_flag(param_name: str, value: float) -> str:
        """Assign clinical abnormality flag based on medical consensus guidelines."""
        name = param_name.lower()
        if "glucose" in name or "glucosa" in name:
            if value < 70.0:
                return "low"
            elif value <= 99.0:
                return "normal"
            elif value <= 125.0:
                return "high"
            else:
                return "critical"
        elif "hba1c" in name or "glicosilada" in name:
            if value < 5.7:
                return "normal"
            elif value <= 6.4:
                return "high"
            else:
                return "critical"
        elif "triglycerides" in name or "trigliceridos" in name:
            if value < 150.0:
                return "normal"
            elif value < 200.0:
                return "high"
            else:
                return "critical"
        elif "hdl" in name:
            if value < 40.0:
                return "low"
            else:
                return "normal"
        elif "ldl" in name:
            if value < 100.0:
                return "normal"
            elif value < 160.0:
                return "high"
            else:
                return "critical"
        return "normal"

    async def parse_and_store_clinical_document(
        self,
        db: AsyncSession,
        document: UploadedDocument,
        raw_text: str,
    ) -> ClinicalRecord:
        """Process OCR text with structured LLM prompt, validate parameters, and persist entities."""
        system_prompt = (
            "You are an expert clinical pathology data extractor. Extract structured parameters from "
            "the provided laboratory report text. Output a JSON object with: "
            "'lab_date' (YYYY-MM-DD), 'parameters' (list of objects with 'parameter_name', 'value' (float), "
            "'unit', 'ref_range_low' (float or null), 'ref_range_high' (float or null))."
        )
        extraction = await self.llm.generate_structured_json(
            system_prompt=system_prompt,
            user_prompt=raw_text,
        )

        parsed_date = None
        if extraction.get("lab_date"):
            try:
                parsed_date = datetime.strptime(extraction["lab_date"], "%Y-%m-%d").date()
            except ValueError:
                parsed_date = date.today()
        else:
            parsed_date = date.today()

        record = ClinicalRecord(
            document_id=document.id,
            user_id=document.user_id,
            lab_date=parsed_date,
            source="ocr",
            raw_extraction=extraction,
            validated=True,
        )
        db.add(record)
        await db.flush()

        raw_params = extraction.get("parameters", [])
        glucose_val = None
        insulin_val = None

        for item in raw_params:
            param_name = str(item.get("parameter_name", "")).strip()
            try:
                val = float(item.get("value", 0.0))
            except (ValueError, TypeError):
                continue

            unit = str(item.get("unit", ""))
            low = float(item["ref_range_low"]) if item.get("ref_range_low") is not None else None
            high = float(item["ref_range_high"]) if item.get("ref_range_high") is not None else None
            flag = self.assign_parameter_flag(param_name, val)

            if "glucose" in param_name.lower() or "glucosa" in param_name.lower():
                glucose_val = val
            if "insulin" in param_name.lower() or "insulina" in param_name.lower():
                insulin_val = val

            param_entity = ClinicalParameter(
                record_id=record.id,
                parameter_name=param_name,
                value=val,
                unit=unit,
                ref_range_low=low,
                ref_range_high=high,
                flag=flag,
            )
            db.add(param_entity)

        # Automatic HOMA-IR synthesis if both markers are present
        if glucose_val and insulin_val:
            homa_score = self.calculate_homa_ir(glucose_val, insulin_val)
            homa_param = ClinicalParameter(
                record_id=record.id,
                parameter_name="homa_ir",
                value=homa_score,
                unit="score",
                ref_range_low=0.0,
                ref_range_high=2.5,
                flag="high" if homa_score >= 2.5 else "normal",
            )
            db.add(homa_param)

        document.status = "processed"
        document.processed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(record)
        return record
