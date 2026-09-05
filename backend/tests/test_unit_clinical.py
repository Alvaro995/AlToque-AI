"""
AlToque AI -- Pruebas Unitarias de Cálculos Clínicos y Bioquímica (F-01, F-09)

Valida fórmulas médicas, cálculo de HOMA-IR, categorización de flags
y métricas antropométricas del paciente.
"""

import pytest
from app.services.clinical_parser_service import ClinicalParserService
from app.services.profile_service import ProfileService
from app.models.user import PatientProfile


class TestClinicalCalculations:
    """Suite de pruebas unitarias para algoritmos clínicos."""

    def test_homa_ir_normal_sensitivity(self):
        """Valida que valores normales de glucosa e insulina generen HOMA-IR < 2.5."""
        # Glucosa: 85 mg/dL, Insulina: 6.0 uIU/mL
        # (85 * 6) / 405 = 1.26
        homa = ClinicalParserService.calculate_homa_ir(85.0, 6.0)
        assert homa == 1.26
        assert homa < 2.50

    def test_homa_ir_insulin_resistance_positive(self):
        """Valida detección de resistencia a la insulina con HOMA-IR >= 2.5."""
        # Glucosa: 110 mg/dL, Insulina: 16.0 uIU/mL
        # (110 * 16) / 405 = 4.35
        homa = ClinicalParserService.calculate_homa_ir(110.0, 16.0)
        assert homa == 4.35
        assert homa >= 2.50

    def test_homa_ir_zero_or_negative_edge_case(self):
        """Valida manejo de valores anómalos o cero sin generar división por cero."""
        assert ClinicalParserService.calculate_homa_ir(0.0, 10.0) == 0.0
        assert ClinicalParserService.calculate_homa_ir(100.0, -5.0) == 0.0

    def test_assign_parameter_flags_glucose(self):
        """Valida umbrales diagnósticos de glucosa en ayunas según la ADA."""
        assert ClinicalParserService.assign_parameter_flag("fasting_glucose", 65.0) == "low"
        assert ClinicalParserService.assign_parameter_flag("fasting_glucose", 88.0) == "normal"
        assert ClinicalParserService.assign_parameter_flag("fasting_glucose", 112.0) == "high"  # Prediabetes
        assert ClinicalParserService.assign_parameter_flag("fasting_glucose", 135.0) == "critical"  # Diabetes

    def test_assign_parameter_flags_hba1c(self):
        """Valida umbrales de hemoglobina glicosilada (HbA1c)."""
        assert ClinicalParserService.assign_parameter_flag("hba1c", 5.2) == "normal"
        assert ClinicalParserService.assign_parameter_flag("hba1c", 5.9) == "high"  # Prediabetes
        assert ClinicalParserService.assign_parameter_flag("hba1c", 6.8) == "critical"  # Rango diabético

    def test_bmi_calculation(self):
        """Valida el cálculo del Índice de Masa Corporal (IMC)."""
        # Peso: 78 kg, Altura: 175 cm -> 78 / (1.75^2) = 25.47 -> 25.5
        bmi = ProfileService.calculate_bmi(weight_kg=78.0, height_cm=175.0)
        assert bmi == 25.5

    def test_bmi_invalid_dimensions(self):
        """Valida que entradas nulas o altura cero retornen None de forma segura."""
        assert ProfileService.calculate_bmi(weight_kg=None, height_cm=175.0) is None
        assert ProfileService.calculate_bmi(weight_kg=70.0, height_cm=0.0) is None
