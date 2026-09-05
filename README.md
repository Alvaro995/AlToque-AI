README.md — AlToque AI
BRODT Hackathon 2026 · Track 3: Future of Health & Wellness

1. Nombre y Misión

AlToque AI es un copiloto inteligente de prevención para personas con prediabetes o riesgo metabólico. Integra una aplicación móvil y un chatbot IA mediante WhatsApp para transformar información clínica, hábitos y rutina diaria en acompañamiento preventivo personalizado, continuo y adaptable.

Misión:
Cerrar la brecha entre la consulta médica y la vida cotidiana mediante una plataforma que facilite el seguimiento longitudinal, la personalización de hábitos y la toma de decisiones preventivas, sin sustituir al profesional de salud.

2. Problema & Enfoque Lean

Problema:
Después de una consulta médica, las recomendaciones preventivas suelen trasladarse a la vida cotidiana sin un mecanismo continuo de seguimiento y personalización. El usuario puede tener dificultades para registrar sus hábitos, interpretar su evolución y adaptar las recomendaciones a su rutina.

Usuario objetivo:
Adultos con prediabetes confirmada o riesgo metabólico relevante que buscan prevenir la progresión hacia diabetes tipo 2.

Propuesta de valor:
AlToque AI centraliza información clínica, hábitos, rutina y objetivos en un perfil longitudinal. La solución utiliza IA y Machine Learning para adaptar el acompañamiento y ofrecer recomendaciones preventivas mediante dos canales complementarios: una aplicación móvil para gestión y análisis, y un chatbot IA para interacción cotidiana mediante WhatsApp.

MVP:
• Registro y autenticación.
• Perfil preventivo.
• Carga de PDF o imágenes de información clínica.
• Extracción de parámetros mediante OCR y modelos multimodales.
• Validación de datos extraídos.
• Registro de hábitos mediante App y WhatsApp.
• Rutina y objetivos adaptables.
• Perfil dinámico de riesgo.
• Modelo predictivo de Machine Learning.
• Explicabilidad mediante SHAP.
• Recomendaciones personalizadas.
• Chatbot IA.
• Sincronización App–WhatsApp mediante backend común.
• Soporte para paciente, persona encargada y médico, con permisos diferenciados.

El sistema utiliza un enfoque de perfil progresivo: la ausencia de un dato no bloquea la plataforma. AlToque adapta el nivel de personalización a la información disponible y puede incorporar nuevos datos progresivamente.

3. Stack Tecnológico & IA

Frontend:
• Flutter / Dart para aplicación móvil.

Backend:
• Python.
• FastAPI.
• REST API.
• Arquitectura modular orientada a MVP.

Base de datos:
• PostgreSQL como fuente única de verdad.
• Redis para cache y tareas auxiliares.
• pgvector para componentes RAG.

Machine Learning:
• Python.
• XGBoost como modelo principal.
• Random Forest como benchmark.
• scikit-learn para procesamiento y evaluación.
• SHAP para explicabilidad.

IA generativa:
• LLM mediante API.
• Function Calling / Tool Calling.
• RAG para recuperación de información validada.
• Modelos multimodales para extracción de información desde documentos e imágenes.

Integraciones:
• WhatsApp Business Cloud API.
• Webhooks.
• Health Connect / HealthKit para datos compatibles de wearables.

Infraestructura:
• Docker.
• Servicios Cloud.
• APIs versionadas.
• Logs y mecanismos básicos de observabilidad.

Arquitectura de IA:
El LLM funciona como orquestador conversacional y no como modelo predictivo. El Machine Learning estima el riesgo, SHAP explica las predicciones, RAG proporciona información fundamentada y el motor de recomendaciones adapta las acciones al perfil del usuario.

4. Setup Local

Requisitos:
• Git.
• Python 3.11+.
• Docker y Docker Compose.
• Flutter SDK.
• Credenciales/API del proveedor LLM.
• Credenciales de WhatsApp Business API para la integración correspondiente.

Clonar el repositorio:

git clone https://github.com/Alvaro995/altoque-ai.git
cd altoque-ai

Configurar variables de entorno mediante un archivo .env:

DATABASE_URL=
REDIS_URL=
LLM_API_KEY=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
SECRET_KEY=

No almacenar credenciales, tokens ni secretos directamente en el repositorio.

Levantar los servicios:

docker compose up --build

Ejecutar el backend:

cd backend
uvicorn main:app --reload

Ejecutar la aplicación móvil:

cd app/mobile
flutter pub get
flutter run

Nota:
Los comandos y variables definitivos podrán ajustarse durante la implementación del MVP según los servicios y credenciales seleccionados.

5. Integrantes & Roles

Alvaro Alberto Ayesta Ramírez
GitHub: @Alvaro995
Rol: Integración y desarrollo del proyecto.

Renzo Arturo Bendezú Castillo
Rol: Integrante del equipo.

Repositorio:
https://github.com/Alvaro995/altoque-ai
