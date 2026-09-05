"""Servicio de orquestación de inferencia predictiva XGBoost y SHAP."""

from typing import Dict, Any, Tuple
import numpy as np

from app.ml.features import FeatureExtractor
from app.ml.model import MetabolicRiskModel
from app.ml.explainability import ModelExplainer


class MLService:
    """Singleton inference and explainability engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
            cls._instance.model = MetabolicRiskModel()
            cls._instance.explainer = ModelExplainer()
        return cls._instance

    def evaluate_risk(
        self,
        clinical_params: Dict[str, float],
        profile_data: Dict[str, Any],
        habit_metrics: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        End-to-end ML prediction pipeline:
        1. Feature dictionary synthesis and imputation.
        2. Vectorization for matrix operations.
        3. Model probability scoring and categorization.
        4. SHAP attribution and clinical translation.
        """
        feature_dict = FeatureExtractor.build_feature_dict(
            clinical_params=clinical_params,
            profile_data=profile_data,
            habit_metrics=habit_metrics,
        )
        vector = FeatureExtractor.to_vector(feature_dict)

        score, level = self.model.predict_risk(vector)

        shap_data = self.explainer.compute_shap_explanations(
            feature_dict=feature_dict,
            feature_vector=vector,
            model_instance=self.model,
        )

        return {
            "risk_score": score,
            "risk_level": level,
            "model_version": self.model.MODEL_VERSION,
            "features_used": feature_dict,
            "shap_values": shap_data["shap_raw"],
            "top_risk_drivers": shap_data["top_risk_drivers"],
            "top_protective_factors": shap_data["top_protective_factors"],
            "narrative_explanation": shap_data["narrative_summary"],
        }
