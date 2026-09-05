"""Servicio de evaluación de amortiguación glucémica y buffer score (F-04)."""

from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.glycemic import FoodLog, FoodItem, BufferEvaluation


class GlycemicBufferService:
    """Evaluates gastric emptying attenuation and macronutrient buffering synergy."""

    @staticmethod
    def evaluate_meal_composition(items: List[Dict[str, Any]]) -> Tuple[float, str, str, bool]:
        """
        Analyze meal components and compute buffer score (0.0 - 10.0),
        alert category, recommendation text, and boolean buffer status.
        """
        has_carb = False
        has_fiber = False
        has_protein = False
        has_fat = False
        has_acid = False

        for item in items:
            cat = str(item.get("category", "")).lower()
            name = str(item.get("name", "")).lower()

            if cat == "carbohydrate" or any(w in name for w in ["arroz", "pan", "papa", "pasta", "fruta", "avena"]):
                has_carb = True
            if cat == "fiber" or any(w in name for w in ["ensalada", "verdura", "brocoli", "espinaca", "chia", "linaza"]):
                has_fiber = True
            if cat == "protein" or any(w in name for w in ["pollo", "huevo", "pescado", "tofu", "carne", "yogur"]):
                has_protein = True
            if cat == "fat" or any(w in name for w in ["palta", "aguacate", "oliva", "nueces", "almendras"]):
                has_fat = True
            if any(w in name for w in ["vinagre", "limon", "fermento"]):
                has_acid = True

        if not has_carb:
            return 8.5, "synergy_ok", "Comida sin carga glucemica preponderante detectada. Perfil estable.", True

        # Base carbohydrate present
        score = 2.0
        if has_fiber:
            score += 3.0
        if has_protein:
            score += 2.5
        if has_fat:
            score += 1.5
        if has_acid:
            score += 1.0

        score = min(10.0, score)

        if score < 4.0:
            alert = "isolated_carb"
            rec = (
                "Alerta de carbohidrato no amortiguado: El consumo de carbohidratos sin acompañamiento "
                "de fibra o proteina acelera el vaciamiento gastrico y eleva la pendiente de glucosa postprandial. "
                "Se sugiere incorporar semillas de chia, frutos secos (15-20g) o una porcion de vegetales verdes."
            )
            has_buffer = False
        elif score < 7.0:
            alert = "partial_buffer"
            rec = (
                "Amortiguacion parcial: La comida cuenta con proteina o grasa, pero un mayor aporte de fibra soluble "
                "reduciria sustancialmente la velocidad de absorcion intestinal de la glucosa."
            )
            has_buffer = True
        elif score < 9.0:
            alert = "synergy_ok"
            rec = (
                "Sinergia glucemica adecuada: Excelente balance de macronutrientes. La presencia conjunta de fibra y "
                "proteina atenua significativamente el pico glucemico postprandial."
            )
            has_buffer = True
        else:
            alert = "acid_boost"
            rec = (
                "Optimizacion glucemica avanzada: La presencia de acidos organicos y fibra maximiza la inhibicion "
                "de alfa-amilasa gastrica, favoreciendo un perfil glucemico aplanado."
            )
            has_buffer = True

        return score, alert, rec, has_buffer

    async def evaluate_and_persist(
        self,
        db: AsyncSession,
        food_log: FoodLog,
    ) -> BufferEvaluation:
        """Evaluate meal items associated with FoodLog and persist BufferEvaluation entity."""
        items_dict = [
            {"name": item.name, "category": item.category}
            for item in food_log.items
        ]
        score, alert, rec, has_buffer = self.evaluate_meal_composition(items_dict)

        evaluation = BufferEvaluation(
            food_log_id=food_log.id,
            has_buffer=has_buffer,
            buffer_score=score,
            alert_type=alert,
            recommendation_text=rec,
        )
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation
