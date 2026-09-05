# AlToque AI

**BRODT Hackathon 2026 · Track 3: Future of Health & Wellness**

Copiloto inteligente de prevención y acompañamiento metabólico para personas con prediabetes o riesgo metabólico confirmado.

---
Link del canva: https://canva.link/u8c6ycxflgkxhru
-
Link de la app: https://gluco-family-guide.lovable.app/

## 1. Nombre y Misión

### AlToque AI

AlToque AI es una plataforma integral de prevención personalizada para personas con prediabetes o riesgo metabólico. Integra una aplicación móvil y un copiloto conversacional inteligente mediante WhatsApp para transformar información clínica, hábitos de alimentación, actividad física y ritmos circadianos en un acompañamiento preventivo continuo, estructurado y adaptable.

### Misión

Cerrar la brecha temporal y operativa entre la consulta médica y la vida cotidiana del paciente, proporcionando un sistema de seguimiento longitudinal, optimización de hábitos basados en evidencia científica y soporte en la toma de decisiones preventivas, **sin sustituir en ningún caso el criterio diagnóstico ni terapéutico del profesional de la salud**.

---

## 2. Problema y Enfoque Lean

### Problema

Tras una consulta médica, las indicaciones de modificación de estilo de vida suelen trasladarse al día a día del paciente sin herramientas de monitoreo continuo ni retroalimentación en tiempo real. 

El paciente enfrenta barreras significativas:
* Dificultad para registrar y cuantificar sus hábitos de manera consistente y sin fricción.
* Falta de comprensión sobre cómo la combinación y el orden de los alimentos influyen en su curva glucémica.
* Horarios laborales rígidos o turnos rotativos que colisionan con las recomendaciones estándar.
* Desconexión entre los resultados de laboratorio (glucosa en ayunas, HbA1c, HOMA-IR) y las acciones cotidianas.
* Falta de integración de su red de apoyo familiar en el proceso preventivo.

### Usuario Objetivo

Adultos con **prediabetes confirmada** (criterios ADA: HbA1c entre 5.7% y 6.4%, o glucosa en ayunas entre 100 y 125 mg/dL) o **síndrome metabólico** que buscan detener la progresión hacia diabetes tipo 2.

### Propuesta de Valor

AlToque AI consolida datos de laboratorio, cronogramas de trabajo, registros de ingesta y actividad física en un **perfil longitudinal continuo**. La solución combina modelos de Machine Learning explicables con IA conversacional a través de dos interfaces complementarias:

* **Aplicación Móvil:** Visualización de tendencias, simulación educativa de curvas glucémicas, gestión de perfiles y coordinación de la red de cuidado.
* **Copiloto IA vía WhatsApp:** Registro conversacional rápido mediante texto o imágenes, recordatorios contextuales y consultas educativas inmediatas.

### Enfoque de Perfil Progresivo

La plataforma implementa un modelo de **perfil progresivo**: la ausencia inicial de parámetros o registros de laboratorio no bloquea el uso del sistema. AlToque AI calibra su nivel de intervención con la información disponible e imputa técnicamente valores de referencia, enriqueciendo las estimaciones conforme el usuario incorpora análisis clínicos y hábitos diarios.

---

## 3. Catálogo Funcional del MVP

El Producto Mínimo Viable se estructura en 5 dominios clínicos y técnicos que abarcan 12 funcionalidades clave:

### Dominio 1: Ingesta, Extracción Inteligente de Datos y Configuración Clínica

| Código | Funcionalidad | Descripción Técnica y Fisiológica |
|---|---|---|
| **F-01** | Extractor y Analizador de Reportes Médicos (*Medical PDF Parser*) | Pipeline de procesamiento de archivos PDF e imágenes de análisis de laboratorio. Extrae glucosa en ayunas, HbA1c, insulina basal, perfil lipídico y calcula automáticamente el índice de resistencia a la insulina (**HOMA-IR**) mediante OCR y extracción estructurada validada con esquemas JSON. |
| **F-02** | Digitalizador de Rutina y Horarios Fijos (*Schedule PDF Ingestion*) | Ingesta de horarios de trabajo, turnos laborales y calendarios semanales para identificar bloques de indisponibilidad y rutinas de vigilia y descanso. |
| **F-03** | Motor de Conciliación de Horarios y Ventanas Metabólicas | Algoritmo que concilia compromisos laborales con una meta de descanso (7 a 8 horas) y calcula ventanas óptimas para alimentación y micro-pausas activas, asegurando un ayuno nocturno reparador. |

### Dominio 2: Motor de Dinámica Glucémica y Comportamiento Alimentario

| Código | Funcionalidad | Descripción Técnica y Fisiológica |
|---|---|---|
| **F-04** | Detector de Carbohidratos Aislados y Buffer Glucémico | Sistema heurístico basado en evidencia clínica que evalúa la composición de cada comida. Detecta carbohidratos no amortiguados y evalúa la presencia de fibra, proteína, lípidos saludables o ácidos orgánicos para mitigar la velocidad de absorción de glucosa. |
| **F-05** | Protocolo de Secuenciación de Alimentos (*Food Sequencing Protocol*) | Interfaz y algoritmo que promueve el orden fisiológico de ingesta: vegetales y fibra primero (inducción de GLP-1 y matriz mucosa), proteínas y grasas segundo (retraso del vaciamiento gástrico), y carbohidratos/almidones al final. |
| **F-06** | Simulador Educativo de Curva Glucémica Postprandial | Modelo matemático cinético (Lehmann-Deutsch) que proyecta y grafica a 180 minutos la curva de glucosa estimada, contrastando la ingesta aislada frente a la ingesta amortiguada y secuenciada. |

### Dominio 3: Hábitos Físicos y Captación Periférica de Glucosa

| Código | Funcionalidad | Descripción Técnica y Fisiológica |
|---|---|---|
| **F-07** | Gatillador de Contracción Muscular Post-Ingesta (*Muscle Glucose Sink Trigger*) | Recordatorio programado entre 30 y 45 minutos después de las comidas principales para inducir la translocación de transportadores **GLUT4** mediante contracción muscular no dependiente de insulina (elevaciones de sóleo en sedestación, caminata ligera). |
| **F-08** | Rutinas de Fuerza Progresiva para Sensibilización Insulínica | Generador de protocolos semanales breves de resistencia enfocados en grandes grupos musculares (cuádriceps, glúteos y espalda), adaptados a perfil estándar o adulto mayor (*senior*). |

### Dominio 4: Perfiles Adaptativos y Red de Cuidado

| Código | Funcionalidad | Descripción Técnica y Fisiológica |
|---|---|---|
| **F-09** | Sistema de Emparejamiento Paciente-Cuidador | Vinculación segura entre el paciente y un familiar o profesional designado, con control granular de permisos (lectura de comidas, parámetros clínicos, alertas). |
| **F-10** | Red de Cuidado y Nudges Asincrónicos | Detección de desviaciones o registros omitidos en ventanas críticas (comidas o actividad física) con despacho de recordatorios amables y no punitivos al cuidador autorizado. |

### Dominio 5: Asistente Conversacional y Soporte a la Consulta

| Código | Funcionalidad | Descripción Técnica y Fisiológica |
|---|---|---|
| **F-11** | Copiloto Conversacional Multicanal con Guardrails Clínicos | Asistente de IA disponible en la aplicación y vía WhatsApp. Integra arquitectura **RAG** con literatura validada (ADA, IDF) y barreras estrictas: prohíbe prescribir fármacos, emitir diagnósticos definitivos y deriva emergencias de forma inmediata. |
| **F-12** | Generador de Reporte Clínico Longitudinal para Consulta Médica | Compilador de datos longitudinales que genera un informe ejecutivo en formato **PDF** para el médico tratante, resumiendo tasas de adherencia a la secuenciación, descanso, actividad y evolución de biomarcadores. |

---

## 4. Arquitectura y Stack Tecnológico

### Separación de Responsabilidades en IA

El sistema desacopla estrictamente la interacción conversacional de los modelos predictivos de riesgo clínico:

| Componente | Tecnología | Responsabilidad Primaria |
|---|---|---|
| **Orquestador Conversacional** | LLM API / Function Calling | Diálogo natural, extracción estructurada JSON y soporte educativo. |
| **Base de Conocimiento Clínico** | pgvector / RAG | Recuperación de guías médicas y literatura de consenso para fundamentar respuestas. |
| **Clasificador de Riesgo Metabólico** | XGBoost (Principal) / Random Forest (Benchmark) | Estimación cuantitativa calibrada de riesgo de progresión a diabetes tipo 2. |
| **Explicabilidad de Modelos** | SHAP (*TreeExplainer*) | Atribución de factores de riesgo y factores protectores traducidos a lenguaje clínico comprensible. |
| **Motor Glucémico y Cinético** | Heurística clínica y cinética diferencial | Evaluación de amortiguación de macronutrientes y simulación de curvas postprandiales. |

### Tecnologías Empleadas

* **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Uvicorn.
* **Bases de Datos:** PostgreSQL 16 con extensión `pgvector`, Redis 7 para caché de baja latencia.
* **Machine Learning y Analítica:** scikit-learn, XGBoost, SHAP, NumPy, Pandas.
* **Procesamiento de Documentos:** Pillow, OCR estructurado, ReportLab para generación de reportes PDF médicos.
* **Canales de Integración:** Meta WhatsApp Business Cloud API (Webhooks bidireccionales).
* **Frontend:** Flutter y Dart (arquitectura multiplataforma para iOS y Android).
* **Infraestructura y Despliegue:** Docker, Docker Compose, variables de entorno securizadas.

---

## 5. Estructura del Repositorio

```
altoque-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                  # Punto de entrada FastAPI y configuración de middleware
│   │   ├── config.py                # Variables de entorno y ajustes validados
│   │   ├── database.py              # Sesión asíncrona SQLAlchemy y conexión PostgreSQL
│   │   ├── dependencies.py          # Inyección de dependencias, autenticación JWT y roles
│   │   ├── models/                  # Entidades relacionales del modelo de datos
│   │   │   ├── user.py              # Usuarios, perfiles antropométricos y emparejamientos
│   │   │   ├── ingestion.py         # Documentos, reportes de laboratorio y bloques de horario
│   │   │   ├── scheduling.py        # Ventanas metabólicas y metas de descanso circadiano
│   │   │   ├── glycemic.py          # Registros de comida, buffer score y simulaciones
│   │   │   ├── physical.py          # Disparadores GLUT4, rutinas de fuerza y registros
│   │   │   ├── care_network.py      # Eventos y alertas para cuidadores autorizados
│   │   │   ├── assistant.py         # Sesiones y mensajes del copiloto conversacional
│   │   │   ├── reporting.py         # Informes clínicos longitudinales
│   │   │   └── risk.py              # Evaluaciones predictivas de riesgo y valores SHAP
│   │   ├── schemas/                 # Esquemas de validación y serialización Pydantic
│   │   ├── services/                # Lógica de negocio y servicios de dominio
│   │   │   ├── auth_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── llm_extraction_service.py
│   │   │   ├── clinical_parser_service.py
│   │   │   ├── schedule_parser_service.py
│   │   │   ├── metabolic_window_service.py
│   │   │   ├── glycemic_buffer_service.py
│   │   │   ├── food_order_service.py
│   │   │   ├── glucose_simulator_service.py
│   │   │   ├── muscle_sink_service.py
│   │   │   ├── strength_planner_service.py
│   │   │   ├── profile_service.py
│   │   │   ├── pairing_service.py
│   │   │   ├── nudge_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── whatsapp_service.py
│   │   │   ├── report_service.py
│   │   │   ├── pdf_generator_service.py
│   │   │   ├── ml_service.py
│   │   │   └── risk_service.py
│   │   ├── ml/                      # Pipeline de ingeniería de features y modelos
│   │   │   ├── features.py          # Extracción, imputación y vectorización
│   │   │   ├── model.py             # Clasificador XGBoost calibrado
│   │   │   ├── explainability.py    # Motor de SHAP y traducción clínica
│   │   │   └── glycemic_model.py    # Modelo cinético de absorción postprandial
│   │   └── api/
│   │       └── v1/                  # Rutas y controladores de la API REST v1
│   ├── tests/                       # Suite de pruebas automatizadas con PyTest
│   │   ├── test_integration_api.py       # Pruebas de integración de endpoints REST (caminos felices y errores críticos)
│   │   ├── test_unit_clinical.py          # Pruebas unitarias de biomarcadores clínicos y cálculos fisiológicos (HOMA-IR, IMC)
│   │   ├── test_unit_clinical_guardrails.py # Pruebas unitarias de guardrails clínicos, exclusión de prescripción y banderas rojas
│   │   ├── test_unit_glycemic_engine.py   # Pruebas unitarias de amortiguación glucémica y modelo cinético postprandial
│   │   └── test_unit_ml.py                # Pruebas unitarias de vectorización, modelo predictivo XGBoost y explicabilidad SHAP
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                            # Especificaciones de ingeniería y arquitectura
│   ├── architecture.md              # Diagramas de flujo y arquitectura C4
│   ├── database_schema.md           # Modelo entidad-relación y diccionario de datos
│   ├── api_design.md                # Especificación técnica de endpoints REST
│   ├── ml_pipeline.md               # Metodología, validación y explicabilidad del modelo ML
│   ├── deployment.md                # Guía de contenedorización y despliegue cloud
│   └── features.md                  # Matriz detallada de funcionalidades clínicas
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 6. Configuración y Ejecución Local

### Requisitos Previos

* Git
* Python 3.11 o superior
* Docker y Docker Compose
* Flutter SDK (para la aplicación móvil cliente)
* Clave de acceso a API de modelos LLM (OpenAI, Gemini o compatible)
* Cuenta de desarrollador y credenciales en Meta for Developers (WhatsApp Business Cloud API)

### Clonar el Repositorio

```bash
git clone https://github.com/Alvaro995/altoque-ai.git
cd altoque-ai
```

### Configuración de Variables de Entorno

Crear el archivo de configuración `.env` a partir de la plantilla proporcionada:

```bash
cp .env.example .env
```

Configurar los valores de las credenciales en el archivo `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/altoque_db
REDIS_URL=redis://localhost:6379/0

LLM_API_KEY=su_clave_de_api
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

WHATSAPP_ACCESS_TOKEN=su_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=su_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=su_whatsapp_verify_token

SECRET_KEY=clave_secreta_para_firma_de_tokens_jwt
```

*Nota de seguridad: No suba claves de acceso, certificados ni credenciales privadas al control de versiones.*

### Despliegue con Docker Compose

Para levantar PostgreSQL, Redis y el servicio backend en un entorno contenedorizado:

```bash
docker compose up --build
```

### Ejecución Local del Backend (Modo Desarrollo)

En caso de requerir ejecución nativa fuera de contenedores:

```bash
cd backend
python -m venv venv
# En Linux/macOS:
source venv/bin/activate
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación interactiva OpenAPI (Swagger) estará disponible en: `http://localhost:8000/docs`

### Suite de Pruebas Automatizadas (Testing y Calidad de Software)

El sistema incluye una suite de pruebas automatizadas con **PyTest** que valida exhaustivamente tanto los caminos felices (*happy paths*) de la plataforma como la respuesta y contención ante casos de error crítico (requerimiento técnico del track de evaluación):

```bash
cd backend
pytest -v tests
```

#### Cobertura de la Suite de Pruebas:

1. **Pruebas de Integración de API (`test_integration_api.py`):**
   * **Camino Feliz (*Happy Path*):** Verificación de estado de salud del sistema (`/health`), optimización automática de secuencias de alimentos según principios fisiológicos (`/api/v1/glycemic/sequence-optimize`), simulación matemática de curvas postprandiales (`/api/v1/glycemic/simulate`), y verificación de suscripción a webhooks de WhatsApp con token y challenge oficial.
   * **Casos de Error Crítico:** Rechazo de accesos no autenticados sin cabecera Bearer (`401 Unauthorized`), bloqueo de peticiones con tokens JWT manipulados o inválidos (`401 Unauthorized`), denegación de suscripciones fraudulentas a webhooks (`403 Forbidden`), y validación de rechazo inmediato ante carga de archivos clínicos vacíos de 0 bytes (`400 Bad Request`).

2. **Pruebas Unitarias Clínicas y Fisiológicas (`test_unit_clinical.py`):**
   * Cálculo exacto y categorización de resistencia a la insulina mediante la fórmula **HOMA-IR** (`(glucosa * insulina) / 405`).
   * Asignación rigurosa de rangos y banderas clínicas (*high*, *low*, *normal*) según directrices internacionales de la ADA para glucosa en ayunas y HbA1c.
   * Estimación de Índice de Masa Corporal (IMC) y control de bordes numéricos (estatura o peso no fisiológicos).

3. **Pruebas Unitarias de Guardrails Clínicos y Seguridad (`test_unit_clinical_guardrails.py`):**
   * Detección y derivación inmediata ante síntomas de bandera roja médica o urgencia (dolor torácico opresivo, disnea, síntomas agudos de neuroglucopenia o hipoglucemia severa).
   * Bloqueo estricto y contención ante solicitudes de prescripción, dosificación o cambio de fármacos (metformina, insulina, sulfonilureas).
   * Permisión fluida de consultas educativas y de estilo de vida sin falsos positivos.

4. **Pruebas Unitarias del Motor Glucémico y Cinética (`test_unit_glycemic_engine.py`):**
   * Identificación de carbohidratos aislados vs. comidas combinadas y sinérgicas.
   * Algoritmo de secuenciación óptima de alimentos (fibra -> proteína/grasa -> almidones).
   * Verificación del modelo cinético postprandial diferencial de **Lehmann-Deutsch** demostrando atenuación del pico glucémico y reducción del área bajo la curva (AUC).

5. **Pruebas Unitarias del Pipeline de Machine Learning (`test_unit_ml.py`):**
   * Extracción e imputación robusta de vectores de características clínicas (enfoque de perfil progresivo).
   * Inferencia del clasificador **XGBoost** y asignación probabilística a categorías de riesgo (*Bajo*, *Moderado*, *Elevado*).
   * Descomposición de explicabilidad local mediante valores **SHAP** y su traducción a factores clínicos interpretables.

### Ejecución de la Aplicación Móvil (Flutter)

```bash
cd app/mobile
flutter pub get
flutter run
```

---

## 7. Integrantes del Proyecto

* **Alvaro Alberto Ayesta Ramírez**
  * GitHub: [@Alvaro995](https://github.com/Alvaro995)
  * Rol: Integración, arquitectura y desarrollo del proyecto.

* **Dante Olivas**
  * GitHub: [@LordPercival241](https://github.com/LordPercival241)
  * Rol: Desarrollo del proyecto.

* **Renzo Arturo Bendezú Castillo**
  * Rol: Desarrollo del proyecto.

* **Christian Esquivel**
  * GitHub: [@coesquivel](https://github.com/coesquivel)
  * Rol: Desarrollo del proyecto.

---

## 8. Repositorio Oficial

El código fuente y las revisiones de control de versiones se encuentran centralizados en:
https://github.com/Alvaro995/altoque-ai

---

## 9. Descargo de Responsabilidad Médica (Medical Disclaimer)

AlToque AI es una herramienta tecnológica orientada exclusivamente a la **educación, prevención y acompañamiento en hábitos de estilo de vida**. 

La información generada, las evaluaciones predictivas de riesgo metabólico y las recomendaciones de secuenciación alimentaria no constituyen un diagnóstico clínico, prescripción farmacológica ni tratamiento médico. El usuario debe consultar siempre a su médico tratante o endocrinólogo antes de iniciar cualquier cambio significativo en su régimen de salud o medicación.
