# AlToque AI

**BRODT Hackathon 2026 · Track 3: Future of Health & Wellness**

---

## 1. Nombre y misión

### AlToque AI

**AlToque AI** es un copiloto inteligente de prevención para personas con prediabetes o riesgo metabólico. Integra una aplicación móvil y un chatbot de IA mediante WhatsApp para transformar información clínica, hábitos y rutina diaria en un acompañamiento preventivo personalizado, continuo y adaptable.

### 🎯 Misión

Cerrar la brecha entre la consulta médica y la vida cotidiana mediante una plataforma que facilite el seguimiento longitudinal, la personalización de hábitos y la toma de decisiones preventivas, **sin sustituir al profesional de salud**.

---

## 2. Problema & enfoque Lean

### Problema

Después de una consulta médica, las recomendaciones preventivas suelen trasladarse a la vida cotidiana sin un mecanismo continuo de seguimiento y personalización.

El usuario puede tener dificultades para:

* Registrar sus hábitos de forma consistente.
* Interpretar su evolución.
* Adaptar las recomendaciones a su rutina.
* Mantener continuidad entre consultas médicas.

### Usuario objetivo

Adultos con **prediabetes confirmada o riesgo metabólico relevante** que buscan prevenir la progresión hacia diabetes tipo 2.

### Propuesta de valor

AlToque AI centraliza información clínica, hábitos, rutina y objetivos en un **perfil longitudinal**.

La solución utiliza **Inteligencia Artificial y Machine Learning** para adaptar el acompañamiento y ofrecer recomendaciones preventivas mediante dos canales complementarios:

* 📱 **Aplicación móvil:** gestión, seguimiento y análisis.
* 💬 **Chatbot IA vía WhatsApp:** interacción cotidiana y registro de información.

### MVP

El Producto Mínimo Viable incluye:

* Registro y autenticación.
* Perfil preventivo.
* Carga de documentos PDF e imágenes con información clínica.
* Extracción de parámetros mediante OCR y modelos multimodales.
* Validación de datos extraídos.
* Registro de hábitos mediante la aplicación y WhatsApp.
* Rutina y objetivos adaptables.
* Perfil dinámico de riesgo.
* Modelo predictivo de Machine Learning.
* Explicabilidad mediante **SHAP**.
* Recomendaciones personalizadas.
* Chatbot de IA.
* Sincronización App–WhatsApp mediante un backend común.
* Soporte para:

  * Paciente.
  * Persona encargada
* Permisos diferenciados según el tipo de usuario.

### Perfil progresivo

El sistema utiliza un enfoque de **perfil progresivo**: la ausencia de un dato no bloquea la plataforma.

AlToque AI adapta el nivel de personalización a la información disponible y permite incorporar nuevos datos progresivamente a medida que el usuario interactúa con la plataforma.

---

## 3. Stack tecnológico & IA

### Frontend

* **Flutter**
* **Dart**

Aplicación móvil multiplataforma.

### Backend

* **Python**
* **FastAPI**
* **REST API**
* Arquitectura modular orientada a MVP.

### Base de datos

* **PostgreSQL** como fuente única de verdad.
* **Redis** para cache y tareas auxiliares.
* **pgvector** para componentes RAG.

### Machine Learning

* **Python**
* **XGBoost** como modelo principal.
* **Random Forest** como benchmark.
* **scikit-learn** para procesamiento y evaluación.
* **SHAP** para explicabilidad de las predicciones.

### IA generativa

* LLM mediante API.
* **Function Calling / Tool Calling**.
* **RAG (Retrieval-Augmented Generation)** para recuperación de información validada.
* Modelos multimodales para extracción de información desde documentos e imágenes.

### Integraciones

* **WhatsApp Business Cloud API**
* Webhooks.
* **Health Connect / HealthKit** para datos compatibles provenientes de wearables.

### Infraestructura

* **Docker**
* Docker Compose.
* Servicios Cloud.
* APIs versionadas.
* Logs y mecanismos básicos de observabilidad.

### Arquitectura de IA

El **LLM funciona como orquestador conversacional**, no como modelo predictivo.

La arquitectura separa las responsabilidades:

| Componente                   | Responsabilidad                              |
| ---------------------------- | -------------------------------------------- |
| **LLM**                      | Orquestación y conversación                  |
| **Machine Learning**         | Estimación del riesgo                        |
| **SHAP**                     | Explicabilidad de las predicciones           |
| **RAG**                      | Recuperación de información fundamentada     |
| **Motor de recomendaciones** | Adaptación de acciones al perfil del usuario |

Esta separación permite que las predicciones de riesgo sean realizadas por modelos especializados y que el LLM se encargue principalmente de la interacción y orquestación.

---

## 4. Setup local

### Requisitos

Antes de comenzar, asegúrate de tener instalado:

* [Git](https://git-scm.com/)
* **Python 3.11+**
* **Docker**
* **Docker Compose**
* **Flutter SDK**
* Credenciales/API del proveedor LLM.
* Credenciales de **WhatsApp Business API** para la integración correspondiente.

### Clonar el repositorio

```bash
git clone https://github.com/Alvaro995/altoque-ai.git
cd altoque-ai
```

### Variables de entorno

Configura las variables de entorno mediante un archivo `.env`:

```env
DATABASE_URL=
REDIS_URL=

LLM_API_KEY=

WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=

SECRET_KEY=
```

> ⚠️ **Importante:** no almacenes credenciales, tokens, API keys ni otros secretos directamente en el repositorio.

### Levantar los servicios

```bash
docker compose up --build
```

### Ejecutar el backend

```bash
cd backend
uvicorn main:app --reload
```

### Ejecutar la aplicación móvil

```bash
cd app/mobile
flutter pub get
flutter run
```

> **Nota:** los comandos, rutas y variables definitivos podrán ajustarse durante la implementación del MVP según los servicios, proveedores y credenciales seleccionados.

---

## 5. Integrantes & roles

### Alvaro Alberto Ayesta Ramírez

* **GitHub:** [@Alvaro995](https://github.com/Alvaro995)
* **Rol:** Integración y desarrollo del proyecto.

### Dante Olivas 

* **GitHub:** [@LordPercival241](https://github.com/LordPercival241)
* **Rol:** Desarrollo del proyecto.


### Renzo Arturo Bendezú Castillo

* **Rol:** Desarrollo del proyecto.

### Christian Esquivel

* **GitHub:** [@coesquivel](https://github.com/coesquivel)
* **Rol:** Desarrollo del proyecto.

---

## 🔗 Repositorio

**GitHub:**
https://github.com/Alvaro995/altoque-ai

---

## ⚕️ Disclaimer

AlToque AI es una herramienta de **prevención y acompañamiento**. No pretende sustituir el diagnóstico, tratamiento ni criterio de un profesional de salud.
