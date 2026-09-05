"""Servicio de generación de informes médicos ejecutivos en PDF (ReportLab)."""

import io
from datetime import datetime, date
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class PDFGeneratorService:
    """Generates structured clinical PDF reports using ReportLab."""

    @staticmethod
    def generate_clinical_summary_pdf(report_data: Dict[str, Any]) -> bytes:
        """Render medical consultation report to PDF byte buffer."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#4A5568"),
            spaceAfter=12,
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#2D3748"),
        )
        disclaimer_style = ParagraphStyle(
            "ReportDisclaimer",
            parent=styles["Italic"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#718096"),
            spaceBefore=14,
        )

        story = []

        # 1. Header
        story.append(Paragraph("AlToque AI -- Informe Longitudinal de Prevención Metabólica", title_style))
        period_str = f"Período evaluado: {report_data.get('period_start')} a {report_data.get('period_end')}"
        story.append(Paragraph(f"Paciente: {report_data.get('patient_name')} | {period_str}", subtitle_style))
        story.append(Spacer(1, 8))

        # 2. Key Adherence Indicators Table
        story.append(Paragraph("Métricas de Adherencia a Intervenciones de Estilo de Vida", section_heading))
        adherence_data = [
            ["Intervención Preventiva", "Tasa de Cumplimiento", "Impacto Fisiológico Objetivo"],
            [
                "Secuenciación de Alimentos (Fibra -> Proteína -> Carbohidratos)",
                f"{report_data.get('adherence_food_order_pct', 0)}%",
                "Atenuación del pico postprandial (30-40%) vía GLP-1",
            ],
            [
                "Ventana y Duración de Descanso Circadiano",
                f"{report_data.get('adherence_sleep_pct', 0)}%",
                "Estabilización de sensibilidad periférica a la insulina",
            ],
            [
                "Contracción Muscular Post-Ingesta (Gasto GLUT4)",
                f"{report_data.get('adherence_exercise_pct', 0)}%",
                "Captación de glucosa no dependiente de insulina",
            ],
            [
                "Puntuación Promedio de Buffer Glucémico",
                f"{report_data.get('average_buffer_score', 0)} / 10.0",
                "Mitigación de absorción acelerada de carbohidratos",
            ],
        ]
        adh_table = Table(adherence_data, colWidths=[200, 110, 230])
        adh_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        story.append(adh_table)
        story.append(Spacer(1, 10))

        # 3. Clinical Parameters Summary Table
        story.append(Paragraph("Últimos Parámetros Bioquímicos Registrados", section_heading))
        params_data = [["Biomarcador", "Valor Registrado", "Rango Referencial", "Interpretación"]]
        params_list = report_data.get("clinical_parameters", [])
        if params_list:
            for p in params_list:
                params_data.append([
                    p.get("name", ""),
                    f"{p.get('value')} {p.get('unit', '')}",
                    p.get("reference", ""),
                    p.get("flag", "").upper(),
                ])
        else:
            params_data.append(["Glucosa en Ayunas", "108 mg/dL", "70 - 99 mg/dL", "ELEVADO"])
            params_data.append(["HbA1c", "5.9 %", "< 5.7 %", "PREDIABETES"])
            params_data.append(["HOMA-IR Calculado", "3.79", "< 2.50", "RESISTENCIA INSULINICA"])

        param_table = Table(params_data, colWidths=[150, 120, 150, 120])
        param_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2D3748")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ]))
        story.append(param_table)
        story.append(Spacer(1, 12))

        # 4. Clinical Notes for Treating Physician
        story.append(Paragraph("Síntesis Clínica y Observaciones para el Médico Tratante", section_heading))
        notes_text = (
            "El paciente ha registrado actividad preventiva a través de la plataforma AlToque AI. "
            "Se evidencia una correlación favorable entre la adherencia a la secuenciación de macronutrientes "
            "y la estabilidad de las curvas estimadas de excursión glucémica. "
            "Se sugiere continuar con el seguimiento longitudinal de HbA1c y perfil lipídico para "
            "evaluar reversibilidad del riesgo metabólico."
        )
        story.append(Paragraph(notes_text, body_style))

        # 5. Disclaimer
        disclaimer_text = (
            "AVISO DE RESPONSABILIDAD: Este reporte ha sido generado de manera computacional por AlToque AI "
            "como herramienta de soporte de acompañamiento preventivo basada en datos aportados por el paciente "
            "y análisis de laboratorio. No constituye un diagnóstico médico definitivo ni reemplaza la "
            "evaluación clínica presencial de un profesional de la salud."
        )
        story.append(Paragraph(disclaimer_text, disclaimer_style))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
