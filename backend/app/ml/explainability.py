"""Motor de explicabilidad SHAP y traducción clínica de factores protectores y de riesgo."""

from typing import Dict, Any, List, Tuple
import numpy as np

from app.ml.features import FeatureExtractor


class ModelExplainer:
    """Computes and translates feature contributions to predictive risk."""

    FEATURE_DESCRIPTIONS = {
        "hba1c": "Nivel de Hemoglobina Glicosilada (HbA1c)",
        "fasting_glucose": "Glucosa plasmática en ayunas",
        "homa_ir": "Índice de Resistencia a la Insulina (HOMA-IR)",
        "bmi": "Índice de Masa Corporal (IMC)",
        "triglycerides": "Nivel de triglicéridos",
        "avg_buffer_score_7d": "Consistencia en amortiguación de comidas",
        "pct_order_confirmed_7d": "Adherencia al orden de ingesta de alimentos",
        "pct_triggers_completed": "Cumplimiento de actividad física post-comida",
        "sleep_target_adherence_7d": "Regularidad de horas de descanso",
    }

    @classmethod
    def compute_shap_explanations(
        cls,
        feature_dict: Dict[str, float],
        feature_vector: np.ndarray,
        model_instance: Any,
    ) -> Dict[str, Any]:
        """
        Derive local feature contribution scores.
        Attempts SHAP TreeExplainer; falls back to linear sensitivity approximation if SHAP is absent.
        """
        contributions: Dict[str, float] = {}

        try:
            import shap
            if model_instance and hasattr(model_instance, "model") and model_instance.model is not None:
                explainer = shap.TreeExplainer(model_instance.model)
                shap_vals = explainer.shap_values(feature_vector)
                # For binary classification, shap_values can be 1D or 2D
                if isinstance(shap_vals, list):
                    vals = shap_vals[1][0]
                elif shap_vals.ndim == 2:
                    vals = shap_vals[0]
                else:
                    vals = shap_vals

                for idx, name in enumerate(FeatureExtractor.FEATURE_NAMES):
                    contributions[name] = round(float(vals[idx]), 3)
            else:
                contributions = cls._heuristic_contributions(feature_dict)
        except Exception:
            contributions = cls._heuristic_contributions(feature_dict)

        # Generate human-readable clinical interpretations
        top_positive, top_protective = cls._rank_factors(contributions, feature_dict)

        return {
            "shap_raw": contributions,
            "top_risk_drivers": top_positive,
            "top_protective_factors": top_protective,
            "narrative_summary": cls._build_narrative(top_positive, top_protective),
        }

    @classmethod
    def _heuristic_contributions(cls, f: Dict[str, float]) -> Dict[str, float]:
        """Approximated feature sensitivities based on standard clinical risk weights."""
        contribs = {}
        contribs["hba1c"] = round((f.get("hba1c", 5.7) - 5.4) * 1.5, 3)
        contribs["fasting_glucose"] = round((f.get("fasting_glucose", 100.0) - 95.0) * 0.04, 3)
        contribs["homa_ir"] = round((f.get("homa_ir", 2.5) - 2.0) * 0.45, 3)
        contribs["bmi"] = round((f.get("bmi", 26.0) - 24.0) * 0.12, 3)
        contribs["triglycerides"] = round((f.get("triglycerides", 150.0) - 130.0) * 0.008, 3)
        contribs["avg_buffer_score_7d"] = round(-(f.get("avg_buffer_score_7d", 6.0) - 5.0) * 0.25, 3)
        contribs["pct_order_confirmed_7d"] = round(-(f.get("pct_order_confirmed_7d", 50.0) - 40.0) * 0.015, 3)
        contribs["pct_triggers_completed"] = round(-(f.get("pct_triggers_completed", 50.0) - 40.0) * 0.02, 3)
        return contribs

    @classmethod
    def _rank_factors(
        cls, contributions: Dict[str, float], features: Dict[str, float]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Separate factors that increase risk from those that protect against it."""
        positives = []
        negatives = []

        for feat, val in contributions.items():
            label = cls.FEATURE_DESCRIPTIONS.get(feat, feat)
            actual_val = features.get(feat)
            item = {"feature": feat, "label": label, "impact": val, "current_value": actual_val}
            if val > 0.05:
                positives.append(item)
            elif val < -0.05:
                negatives.append(item)

        positives.sort(key=lambda x: x["impact"], reverse=True)
        negatives.sort(key=lambda x: x["impact"])

        return positives[:3], negatives[:3]

    @classmethod
    def _build_narrative(
        cls, positive_factors: List[Dict[str, Any]], protective_factors: List[Dict[str, Any]]
    ) -> str:
        """Compose clear, actionable medical summary."""
        parts = []
        if positive_factors:
            main_driver = positive_factors[0]
            parts.append(
                f"El principal factor que incrementa el riesgo metabolico actual es {main_driver['label']} "
                f"(impacto estimado de +{abs(round(main_driver['impact'] * 10, 1))} puntos de riesgo)."
            )
        if protective_factors:
            main_shield = protective_factors[0]
            parts.append(
                f"Por otro lado, {main_shield['label']} está actuando de forma protectora "
                f"atenuando el riesgo en -{abs(round(main_shield['impact'] * 10, 1))} puntos."
            )
        if not parts:
            return "Sus indicadores se encuentran en un balance metabolico estable."
        return " ".join(parts)
