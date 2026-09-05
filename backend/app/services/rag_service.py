"""Servicio de recuperación clínica aumentada (RAG) basada en guías ADA/IDF."""

from typing import List, Dict, Any


class RAGService:
    """Clinical knowledge base index and context retrieval engine."""

    CLINICAL_KNOWLEDGE_BASE = [
        {
            "id": "kb_secuencia",
            "keywords": ["orden", "secuencia", "empezar", "primero", "fibra", "arroz", "carbohidrato"],
            "title": "Protocolo de Secuenciacion de Macronutrientes (Weill Cornell)",
            "content": (
                "Consumir vegetales y fibra 10 minutos antes de los carbohidratos reduce el pico de glucosa "
                "postprandial entre un 30% y 40% y el pico de insulina en un 48%. Esto se debe al retraso en "
                "el vaciamiento gastrico mediado por GLP-1 y a la creacion de una matriz mucosa intestinal de absorcion lenta."
            ),
        },
        {
            "id": "kb_buffer",
            "keywords": ["amortiguar", "combinar", "buffer", "fruta", "pan", "grasa", "proteina"],
            "title": "Buffer Glucemico y Co-ingestion de Macronutrientes",
            "content": (
                "La adicion de proteinas magras (huevos, yogur griego, legumbres) o lipidos insaturados (palta, frutos secos, "
                "aceite de oliva) a una fuente de almidon modula el indice glucemico total de la comida, "
                "previniendo picos agudos y caidas de hipoglucemia reactiva."
            ),
        },
        {
            "id": "kb_soleo",
            "keywords": ["soleo", "ejercicio", "caminar", "postprandial", "despues de comer", "sentadillas"],
            "title": "Translocacion de GLUT4 y Contraccion Muscular Postprandial",
            "content": (
                "La contraccion del musculo soleo o una caminata de 10-15 minutos entre 30 y 45 minutos despues de comer "
                "activa la proteina quinasa activada por AMP (AMPK). Esto moviliza transportadores GLUT4 a la membrana "
                "celular de forma independiente a la insulina, captando glucosa serica directamente."
            ),
        },
        {
            "id": "kb_homa_ir",
            "keywords": ["homa", "insulina", "resistencia", "laboratorio", "analisis", "hba1c"],
            "title": "Valores de Referencia HOMA-IR y Hemoglobina Glicosilada",
            "content": (
                "Un indice HOMA-IR superior a 2.5 indica resistencia a la insulina periferica. Una HbA1c entre 5.7% y 6.4% "
                "define prediabetes segun los criterios de la ADA. En este rango, intervenciones intensivas de estilo de vida "
                "revierten el riesgo de progresion a diabetes tipo 2 en mas del 58%."
            ),
        },
    ]

    async def retrieve_relevant_context(self, user_query: str) -> str:
        """Retrieve most relevant clinical snippets for given conversational prompt."""
        query_words = set(user_query.lower().split())
        scored_docs = []

        for doc in self.CLINICAL_KNOWLEDGE_BASE:
            score = sum(1 for kw in doc["keywords"] if kw in query_words or any(kw in word for word in query_words))
            if score > 0:
                scored_docs.append((score, doc["title"], doc["content"]))

        scored_docs.sort(key=lambda x: x[0], reverse=True)

        if not scored_docs:
            return "Informacion clinica de consenso: El control glucemico preventivo se fundamenta en regularidad horaria y balance de macronutrientes."

        context_snippets = [f"[{item[1]}]: {item[2]}" for item in scored_docs[:2]]
        return "\n".join(context_snippets)
