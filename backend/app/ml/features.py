"""Pipeline de ingeniería de características, imputación y vectorización."""

from datetime import date
from typing import Dict, Any, List, Optional
import numpy as np


class FeatureExtractor:
    """Extracts standardized feature vectors for metabolic risk scoring."""

    FEATURE_NAMES = [
        "hba1c",
        "fasting_glucose",
        "total_cholesterol",
        "hdl_cholesterol",
        "ldl_cholesterol",
        "triglycerides",
        "fasting_insulin",
        "homa_ir",
        "age",
        "sex_male",
        "bmi",
        "activity_sedentary",
        "activity_light",
        "activity_moderate",
        "activity_active",
        "avg_buffer_score_7d",
        "pct_order_confirmed_7d",
        "pct_triggers_completed",
        "sleep_target_adherence_7d",
    ]

    MEDIANS = {
        "hba1c": 5.8,
        "fasting_glucose": 102.0,
        "total_cholesterol": 195.0,
        "hdl_cholesterol": 44.0,
        "ldl_cholesterol": 125.0,
        "triglycerides": 155.0,
        "fasting_insulin": 12.0,
        "homa_ir": 3.02,
        "age": 48.0,
        "sex_male": 1.0,
        "bmi": 27.5,
        "activity_sedentary": 0.0,
        "activity_light": 1.0,
        "activity_moderate": 0.0,
        "activity_active": 0.0,
        "avg_buffer_score_7d": 6.5,
        "pct_order_confirmed_7d": 50.0,
        "pct_triggers_completed": 60.0,
        "sleep_target_adherence_7d": 75.0,
    }

    @classmethod
    def build_feature_dict(
        cls,
        clinical_params: Dict[str, float],
        profile_data: Dict[str, Any],
        habit_metrics: Dict[str, float],
    ) -> Dict[str, float]:
        """Construct raw dictionary of normalized features."""
        features: Dict[str, float] = {}

        # 1. Clinical
        for k in [
            "hba1c", "fasting_glucose", "total_cholesterol", "hdl_cholesterol",
            "ldl_cholesterol", "triglycerides", "fasting_insulin", "homa_ir"
        ]:
            val = clinical_params.get(k)
            features[k] = float(val) if val is not None else cls.MEDIANS[k]

        # 2. Profile
        birth_date = profile_data.get("birth_date")
        if birth_date:
            if isinstance(birth_date, str):
                try:
                    birth_date = date.fromisoformat(birth_date)
                    age = (date.today() - birth_date).days // 365
                except ValueError:
                    age = cls.MEDIANS["age"]
            elif isinstance(birth_date, date):
                age = (date.today() - birth_date).days // 365
            else:
                age = cls.MEDIANS["age"]
        else:
            age = cls.MEDIANS["age"]
        features["age"] = float(age)

        sex = str(profile_data.get("sex", "male")).lower()
        features["sex_male"] = 1.0 if sex == "male" else 0.0

        weight = profile_data.get("weight_kg")
        height = profile_data.get("height_cm")
        if weight and height and height > 0:
            h_m = height / 100.0
            bmi = round(weight / (h_m * h_m), 1)
        else:
            bmi = cls.MEDIANS["bmi"]
        features["bmi"] = float(bmi)

        act = str(profile_data.get("activity_level", "sedentary")).lower()
        features["activity_sedentary"] = 1.0 if act == "sedentary" else 0.0
        features["activity_light"] = 1.0 if act == "light" else 0.0
        features["activity_moderate"] = 1.0 if act == "moderate" else 0.0
        features["activity_active"] = 1.0 if act == "active" else 0.0

        # 3. Habits and Adherence
        features["avg_buffer_score_7d"] = float(habit_metrics.get("avg_buffer_score_7d", cls.MEDIANS["avg_buffer_score_7d"]))
        features["pct_order_confirmed_7d"] = float(habit_metrics.get("pct_order_confirmed_7d", cls.MEDIANS["pct_order_confirmed_7d"]))
        features["pct_triggers_completed"] = float(habit_metrics.get("pct_triggers_completed", cls.MEDIANS["pct_triggers_completed"]))
        features["sleep_target_adherence_7d"] = float(habit_metrics.get("sleep_target_adherence_7d", cls.MEDIANS["sleep_target_adherence_7d"]))

        return features

    @classmethod
    def to_vector(cls, feature_dict: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary into 2D numpy array suitable for sklearn / XGBoost."""
        vector = [feature_dict[name] for name in cls.FEATURE_NAMES]
        return np.array([vector], dtype=np.float32)
