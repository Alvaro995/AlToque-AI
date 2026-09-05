class RiskService:


    @staticmethod
    def calculate_risk(data):

        score = 0


        # HbA1c
        if data.hba1c >= 6.5:
            score += 40

        elif data.hba1c >= 5.7:
            score += 25


        # Glucosa ayunas
        if data.glucose >= 126:
            score += 30

        elif data.glucose >= 100:
            score += 15


        # Actividad física
        if data.weekly_activity_minutes < 150:
            score += 20


        # IMC
        bmi = data.weight / (data.height ** 2)

        if bmi >= 30:
            score += 15


        if score >= 70:

            level = "high"

            message = (
                "Existe un riesgo metabólico elevado. "
                "Se recomienda seguimiento clínico."
            )


        elif score >= 40:

            level = "moderate"

            message = (
                "Presentas factores asociados a riesgo metabólico. "
                "Mejorar actividad física y hábitos alimentarios."
            )


        else:

            level = "low"

            message = (
                "Tu perfil actual presenta menor riesgo metabólico."
            )


        return {
            "risk_score": score,
            "risk_level": level,
            "message": message
        }