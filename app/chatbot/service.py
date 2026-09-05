from sqlalchemy.orm import Session

from app.profiles.repository import ProfileRepository



class ChatbotService:


    @staticmethod
    def generate_response(
        db: Session,
        user_id: int,
        message: str
    ):


        # Obtener perfil clínico del usuario
        profile = ProfileRepository.get_by_user(
            db=db,
            user_id=user_id
        )


        text = message.lower()


        if "arroz" in text:


            if profile:

                response = (
                    f"Según tu perfil metabólico, "
                    f"tu HbA1c registrada es {profile.hba1c}%. "
                    "Puedes consumir arroz, pero recomendamos "
                    "acompañarlo con verduras y proteína para "
                    "reducir el impacto glucémico."
                )

            else:

                response = (
                    "Puedes consumir arroz, pero recomendamos "
                    "acompañarlo con verduras y proteína para "
                    "reducir el impacto glucémico."
                )



        elif "ejercicio" in text:


            response = (
                "Una caminata de 10 a 15 minutos después "
                "de comer puede ayudar a mejorar el control "
                "de glucosa mediante la actividad muscular."
            )



        elif "glucosa" in text:


            if profile:

                response = (
                    f"Tu última glucosa registrada es "
                    f"{profile.glucose} mg/dL. "
                    "Es importante mantener seguimiento "
                    "de tus valores metabólicos."
                )

            else:

                response = (
                    "Aún no tengo datos de glucosa "
                    "registrados en tu perfil."
                )



        else:


            response = (
                "Estoy analizando tu consulta considerando "
                "tu perfil metabólico."
            )



        return {
            "response": response
        }