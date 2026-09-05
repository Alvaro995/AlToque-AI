"""Servicio de simulación matemática de curvas postprandiales (F-06)."""

import math
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.glycemic import FoodLog, GlucoseSimulation


class GlucoseSimulatorService:
    """Mathematical simulation of postprandial glycemic excursions and peak attenuation."""

    @staticmethod
    def generate_curves(
        baseline_glucose: float = 95.0,
        carb_load_grams: float = 50.0,
        buffer_score: float = 7.5,
    ) -> Dict[str, Any]:
        """
        Generate time-series curve points across 180 minutes post-ingestion.
        Returns isolated carb profile vs buffered meal profile.
        """
        time_points = [0, 15, 30, 45, 60, 75, 90, 105, 120, 150, 180]

        # Isolated carbohydrate curve parameters (rapid absorption, high peak, rapid crash)
        isolated_peak_amplitude = min(85.0, carb_load_grams * 1.3)
        isolated_peak_time = 40.0  # minutes

        # Buffered curve parameters (attenuated amplitude, delayed peak, gradual return)
        # buffer_score 0-10 dampens peak by up to 45%
        buffering_factor = max(0.15, min(0.48, (buffer_score / 10.0) * 0.45))
        buffered_peak_amplitude = isolated_peak_amplitude * (1.0 - buffering_factor)
        buffered_peak_time = 65.0  # minutes

        isolated_points: List[Dict[str, float]] = []
        buffered_points: List[Dict[str, float]] = []

        auc_isolated = 0.0
        auc_buffered = 0.0

        for t in time_points:
            # Lognormal-like asymmetric excursion model for isolated carbs
            if t == 0:
                g_iso = baseline_glucose
            else:
                # Shape function: (t / peak_t) * exp(1 - t / peak_t)
                scale_iso = (t / isolated_peak_time) * math.exp(1.0 - (t / isolated_peak_time))
                # Slight undershoot post 120 min (reactive dip)
                undershoot = -4.0 if t >= 120 else 0.0
                g_iso = baseline_glucose + (isolated_peak_amplitude * scale_iso) + undershoot

            # Buffered model: broader dispersion, lowered peak
            if t == 0:
                g_buf = baseline_glucose
            else:
                scale_buf = (t / buffered_peak_time) * math.exp(1.0 - (t / buffered_peak_time))
                g_buf = baseline_glucose + (buffered_peak_amplitude * scale_buf)

            val_iso = round(max(baseline_glucose - 10.0, g_iso), 1)
            val_buf = round(max(baseline_glucose, g_buf), 1)

            isolated_points.append({"time_min": t, "glucose_mg_dl": val_iso})
            buffered_points.append({"time_min": t, "glucose_mg_dl": val_buf})

            auc_isolated += val_iso * 15.0
            auc_buffered += val_buf * 15.0

        peak_iso = max(p["glucose_mg_dl"] for p in isolated_points)
        peak_buf = max(p["glucose_mg_dl"] for p in buffered_points)
        peak_delta_pct = round(((peak_iso - peak_buf) / max(1.0, (peak_iso - baseline_glucose))) * 100.0, 1)

        return {
            "baseline_glucose": baseline_glucose,
            "isolated_curve": isolated_points,
            "buffered_curve": buffered_points,
            "peak_isolated_mg_dl": peak_iso,
            "peak_buffered_mg_dl": peak_buf,
            "peak_reduction_pct": peak_delta_pct,
            "auc_reduction_pct": round(((auc_isolated - auc_buffered) / auc_isolated) * 100.0, 1),
            "clinical_interpretation": (
                f"La combinacion equilibrada y el orden de los alimentos disminuye el pico glucemico maximo "
                f"en un {peak_delta_pct}%, protegiendo la funcion de las celulas beta pancreaticas y reduciendo "
                f"el estres oxidativo endotelial."
            ),
        }

    async def simulate_for_food_log(
        self,
        db: AsyncSession,
        food_log: FoodLog,
        baseline_glucose: float = 95.0,
    ) -> GlucoseSimulation:
        """Execute simulation based on food log buffer evaluation and store result."""
        buffer_score = 5.0
        if food_log.buffer_evaluation:
            buffer_score = food_log.buffer_evaluation.buffer_score

        sim_data = self.generate_curves(
            baseline_glucose=baseline_glucose,
            carb_load_grams=50.0,
            buffer_score=buffer_score,
        )

        simulation = GlucoseSimulation(
            food_log_id=food_log.id,
            curve_isolated={"points": sim_data["isolated_curve"]},
            curve_buffered={"points": sim_data["buffered_curve"]},
            peak_reduction_pct=sim_data["peak_reduction_pct"],
        )
        db.add(simulation)
        await db.commit()
        await db.refresh(simulation)
        return simulation
