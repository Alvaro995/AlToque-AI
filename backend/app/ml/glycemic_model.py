"""Modelo cinético postprandial diferencial de dos compartimentos (Lehmann-Deutsch)."""

import math
from typing import List, Dict, Any


class GlycemicKineticModel:
    """Simulates 2-compartment glucose dynamics following meal ingestion."""

    @staticmethod
    def simulate_excursion(
        fasting_glucose: float,
        carb_grams: float,
        buffer_coefficient: float,  # 0.0 (unbuffered) to 1.0 (fully buffered)
        exercise_triggered: bool = False,
    ) -> List[Dict[str, float]]:
        """
        Calculates glucose concentration G(t) over 180 minutes:
        G(t) = G_base + G_max * (t / t_max)^alpha * exp(alpha * (1 - t / t_max)) - clearance_rate(t)
        """
        # Time to peak is delayed by buffering (40 min -> 65 min)
        t_max = 38.0 + (buffer_coefficient * 25.0)
        # Peak amplitude is dampened by buffering (up to 40% reduction) and exercise (additional 10%)
        dampening = (1.0 - (buffer_coefficient * 0.38)) * (0.90 if exercise_triggered else 1.0)
        g_max = min(80.0, carb_grams * 1.25) * dampening

        alpha = 1.35  # Skewness parameter for gastrointestinal transit

        timeline = []
        for t in range(0, 185, 15):
            if t == 0:
                gt = fasting_glucose
            else:
                ratio = t / t_max
                shape = (ratio ** alpha) * math.exp(alpha * (1.0 - ratio))
                # Exercise enhances clearance between 30 and 90 min
                exercise_drop = 0.0
                if exercise_triggered and 30 <= t <= 90:
                    exercise_drop = 8.0 * math.sin((t - 30) / 60.0 * math.pi)

                gt = fasting_glucose + (g_max * shape) - exercise_drop

            timeline.append({
                "time_min": t,
                "glucose_mg_dl": round(max(fasting_glucose - 5.0, gt), 1),
            })

        return timeline
