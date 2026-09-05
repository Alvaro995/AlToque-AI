"""
AlToque AI -- Pruebas Unitarias del Pipeline de Machine Learning

Valida la extracción de features, imputación por mediana, inferencia del clasificador
y cálculo de atribuciones explicables SHAP.
"""

import pytest
import numpy as np
from app.ml.features import FeatureExtractor
from app.ml.model import MetabolicRiskModel
from app.ml.explainability import ModelExplainer


class TestMLPipeline:
    """Suite de validación para el pipeline de Machine Learning."""

    def test_feature_extractor_with_imputation(self):
        """Valida que valores clínicos faltantes sean imputados con medianas de población."""
        features = FeatureExtractor.build_feature_dict(
            clinical_params={"hba1c": 6.1},  # Solo un dato disponible
            profile_data={"sex": "male", "weight_kg": 80.0, "height_cm": 178.0},
            habit_metrics={},
        )

        assert features["hba1c"] == 6.1
        # fasting_glucose ausente debe tener la mediana poblacional
        assert features["fasting_glucose"] == FeatureExtractor.MEDIANS["fasting_glucose"]
        assert features["bmi"] == 25.2
        assert len(features) == len(FeatureExtractor.FEATURE_NAMES)

    def test_feature_vector_shape(self):
        """Valida conversión a matriz NumPy 2D compatible con XGBoost."""
        features = FeatureExtractor.build_feature_dict(
            clinical_params={}, profile_data={}, habit_metrics={}
        )
        vec = FeatureExtractor.to_vector(features)
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (1, len(FeatureExtractor.FEATURE_NAMES))

    def test_model_prediction_range_and_category(self):
        """Valida que la predicción de riesgo esté acotada entre 0 y 100 y categorizada."""
        model = MetabolicRiskModel()
        features = FeatureExtractor.build_feature_dict(
            clinical_params={"hba1c": 6.3, "fasting_glucose": 118.0, "homa_ir": 3.8},
            profile_data={"weight_kg": 95.0, "height_cm": 170.0},
            habit_metrics={"avg_buffer_score_7d": 3.5},
        )
        vec = FeatureExtractor.to_vector(features)
        score, level = model.predict_risk(vec)

        assert 0.0 <= score <= 100.0
        assert level in ["low", "moderate", "high", "critical"]

    def test_shap_explanation_translation(self):
        """Valida traducción de SHAP a narrativa comprensible en español."""
        model = MetabolicRiskModel()
        features = FeatureExtractor.build_feature_dict(
            clinical_params={"hba1c": 6.2}, profile_data={}, habit_metrics={}
        )
        vec = FeatureExtractor.to_vector(features)
        shap_data = ModelExplainer.compute_shap_explanations(
            feature_dict=features, feature_vector=vec, model_instance=model
        )

        assert "narrative_summary" in shap_data
        assert isinstance(shap_data["narrative_summary"], str)
        assert len(shap_data["narrative_summary"]) > 10
