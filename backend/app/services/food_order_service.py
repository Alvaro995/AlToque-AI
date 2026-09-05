"""Servicio del protocolo de secuenciación óptima de alimentos (F-05)."""

from typing import List, Dict, Any


class FoodOrderService:
    """Computes physiological macronutrient sequencing and assesses sequence compliance."""

    PRIORITY_MAP = {
        "fiber": 1,
        "fat": 2,
        "protein": 2,
        "mixed": 2,
        "carbohydrate": 3,
    }

    @classmethod
    def get_optimal_sequence(cls, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort items into the optimal chronological ingestion sequence:
        1. Fibers & non-starchy vegetables (slows mucosal absorption via mesh network).
        2. Proteins and healthy fats (triggers CCK/GLP-1 release and slows gastric motility).
        3. Carbohydrates and starches (consumed when absorption capacity is buffered).
        """
        def get_priority(item: Dict[str, Any]) -> int:
            cat = str(item.get("category", "carbohydrate")).lower()
            return cls.PRIORITY_MAP.get(cat, 2)

        sorted_items = sorted(items, key=get_priority)
        sequenced = []
        for idx, item in enumerate(sorted_items, start=1):
            sequenced.append({
                **item,
                "recommended_position": idx,
                "stage": "1. Fibra y vegetales" if get_priority(item) == 1 else (
                    "2. Proteinas y grasas saludables" if get_priority(item) == 2 else "3. Carbohidratos y almidones"
                ),
            })
        return sequenced

    @classmethod
    def calculate_order_compliance(cls, items_with_user_order: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate user adherence to the sequencing protocol based on logged order_position.
        Returns compliance percentage and clinical feedback.
        """
        if len(items_with_user_order) < 2:
            return {
                "compliance_score_pct": 100.0,
                "adherent": True,
                "feedback": "Comida de componente unico o simplificado.",
            }

        inversions = 0
        total_pairs = 0

        # Check all pairs (i, j) where i was eaten before j
        for i in range(len(items_with_user_order)):
            for j in range(i + 1, len(items_with_user_order)):
                item_a = items_with_user_order[i]
                item_b = items_with_user_order[j]

                pos_a = item_a.get("order_position", i + 1)
                pos_b = item_b.get("order_position", j + 1)

                prio_a = cls.PRIORITY_MAP.get(str(item_a.get("category", "carbohydrate")).lower(), 2)
                prio_b = cls.PRIORITY_MAP.get(str(item_b.get("category", "carbohydrate")).lower(), 2)

                total_pairs += 1
                # If item_a was eaten before item_b, but item_a has higher priority number (e.g. carb before fiber)
                if (pos_a < pos_b and prio_a > prio_b) or (pos_a > pos_b and prio_a < prio_b):
                    inversions += 1

        compliance_pct = max(0.0, round(100.0 * (1.0 - (inversions / max(1, total_pairs))), 1))
        is_adherent = compliance_pct >= 75.0

        if is_adherent:
            feedback = (
                "Excelente adherencia al protocolo de secuenciacion. Consumir la fibra y proteina "
                "antes de los almidones aplanara la curva glucemica postprandial."
            )
        else:
            feedback = (
                "Inversion en la secuencia detectada: El consumo de carbohidratos previo a la fibra "
                "incrementa la velocidad de absorcion intestinal. Para la proxima comida, inicie con los vegetales."
            )

        return {
            "compliance_score_pct": compliance_pct,
            "adherent": is_adherent,
            "feedback": feedback,
        }
