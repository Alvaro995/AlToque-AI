"""
AlToque AI -- Pruebas Unitarias del Motor Glucémico y Secuenciación (F-04, F-05, F-06)

Valida la detección de carbohidratos aislados, amortiguación de macronutrientes,
adherencia a la secuenciación de alimentos y atenuación de curvas cinéticas.
"""

import pytest
from app.services.glycemic_buffer_service import GlycemicBufferService
from app.services.food_order_service import FoodOrderService
from app.services.glucose_simulator_service import GlucoseSimulatorService
from app.ml.glycemic_model import GlycemicKineticModel


class TestGlycemicEngine:
    """Suite de validación para el motor glucémico y modelos cinéticos."""

    def test_isolated_carbohydrate_detection(self):
        """Valida que una comida compuesta únicamente por carbohidratos dispare alerta crítica."""
        isolated_meal = [{"name": "Pan blanco", "category": "carbohydrate"}]
        score, alert, rec, has_buffer = GlycemicBufferService.evaluate_meal_composition(isolated_meal)

        assert alert == "isolated_carb"
        assert score < 4.0
        assert has_buffer is False
        assert "no amortiguado" in rec.lower()

    def test_synergistic_buffered_meal(self):
        """Valida que la co-ingestión de fibra y proteína genere una amortiguación óptima."""
        buffered_meal = [
            {"name": "Espinaca y brócoli", "category": "fiber"},
            {"name": "Pechuga de pollo", "category": "protein"},
            {"name": "Palta / aguacate", "category": "fat"},
            {"name": "Arroz integral", "category": "carbohydrate"},
        ]
        score, alert, rec, has_buffer = GlycemicBufferService.evaluate_meal_composition(buffered_meal)

        assert alert in ["synergy_ok", "acid_boost"]
        assert score >= 7.0
        assert has_buffer is True

    def test_optimal_food_sequencing_order(self):
        """Valida que el optimizador ordene estrictamente: Fibra -> Proteína/Grasa -> Carbohidratos."""
        unordered_items = [
            {"name": "Arroz blanco", "category": "carbohydrate"},
            {"name": "Ensalada verde", "category": "fiber"},
            {"name": "Pescado al horno", "category": "protein"},
        ]
        sequenced = FoodOrderService.get_optimal_sequence(unordered_items)

        # Posición 1 debe ser fibra
        assert sequenced[0]["category"] == "fiber"
        assert sequenced[0]["name"] == "Ensalada verde"

        # Posición 2 debe ser proteína
        assert sequenced[1]["category"] == "protein"

        # Posición 3 debe ser carbohidrato
        assert sequenced[2]["category"] == "carbohydrate"
        assert sequenced[2]["name"] == "Arroz blanco"

    def test_food_sequencing_compliance_happy_path(self):
        """Valida cumplimiento al 100% cuando el usuario respeta el orden fisiológico."""
        adherent_meal = [
            {"name": "Vegetales", "category": "fiber", "order_position": 1},
            {"name": "Huevo revuelto", "category": "protein", "order_position": 2},
            {"name": "Tostada", "category": "carbohydrate", "order_position": 3},
        ]
        result = FoodOrderService.calculate_order_compliance(adherent_meal)
        assert result["compliance_score_pct"] == 100.0
        assert result["adherent"] is True

    def test_food_sequencing_compliance_inverted_order(self):
        """Valida penalización y alerta educativa cuando el usuario invierte el orden."""
        inverted_meal = [
            {"name": "Tostada dulce", "category": "carbohydrate", "order_position": 1},
            {"name": "Ensalada", "category": "fiber", "order_position": 2},
        ]
        result = FoodOrderService.calculate_order_compliance(inverted_meal)
        assert result["compliance_score_pct"] < 75.0
        assert result["adherent"] is False
        assert "Inversion" in result["feedback"]

    def test_glucose_curve_simulation_peak_reduction(self):
        """Valida que la simulación postprandial reduzca el pico máximo entre un 20% y un 50%."""
        sim = GlucoseSimulatorService.generate_curves(
            baseline_glucose=95.0,
            carb_load_grams=50.0,
            buffer_score=8.0,
        )
        assert sim["peak_isolated_mg_dl"] > sim["peak_buffered_mg_dl"]
        assert 20.0 <= sim["peak_reduction_pct"] <= 55.0
        assert sim["auc_reduction_pct"] > 0.0

    def test_lehmann_deutsch_kinetic_model(self):
        """Valida modelo cinético con efecto de gasto GLUT4 por ejercicio postprandial."""
        curve_rest = GlycemicKineticModel.simulate_excursion(
            fasting_glucose=90.0, carb_grams=45.0, buffer_coefficient=0.8, exercise_triggered=False
        )
        curve_active = GlycemicKineticModel.simulate_excursion(
            fasting_glucose=90.0, carb_grams=45.0, buffer_coefficient=0.8, exercise_triggered=True
        )

        assert len(curve_rest) == len(curve_active)
        # A los 60 minutos el ejercicio debe reducir la concentración respecto al reposo
        g_rest_60 = next(p["glucose_mg_dl"] for p in curve_rest if p["time_min"] == 60)
        g_active_60 = next(p["glucose_mg_dl"] for p in curve_active if p["time_min"] == 60)
        assert g_active_60 < g_rest_60
