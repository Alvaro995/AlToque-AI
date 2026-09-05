# Diseno de API REST v1 -- AlToque AI

## Convenciones

- Base URL: `/api/v1`
- Autenticacion: Bearer Token (JWT)
- Content-Type: `application/json` (excepto upload de archivos)
- Paginacion: `?page=1&size=20`
- Respuestas de error: `{"detail": "message", "code": "ERROR_CODE"}`

---

## Autenticacion

| Metodo | Ruta | Descripcion | Auth |
|--------|------|-------------|------|
| POST | `/auth/register` | Registro de usuario con rol | No |
| POST | `/auth/login` | Autenticacion, retorna access + refresh token | No |
| POST | `/auth/refresh` | Renovar access token | Refresh |
| GET | `/auth/me` | Datos del usuario autenticado | Si |

---

## Ingestion (F-01, F-02)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| POST | `/documents/upload` | F-01, F-02 | Subir PDF o imagen (multipart/form-data). Campo `doc_type`: clinical o schedule | Si |
| GET | `/documents` | F-01, F-02 | Listar documentos del usuario | Si |
| GET | `/documents/{id}/status` | F-01, F-02 | Estado de procesamiento del documento | Si |
| GET | `/clinical-records` | F-01 | Listar registros clinicos extraidos | Si |
| GET | `/clinical-records/{id}` | F-01 | Detalle del registro con parametros extraidos | Si |
| POST | `/clinical-records/{id}/validate` | F-01 | Confirmar o corregir datos extraidos | Si |
| GET | `/schedule-blocks` | F-02 | Listar bloques de horario del usuario | Si |
| PUT | `/schedule-blocks/{id}` | F-02 | Ajustar bloque de horario manualmente | Si |
| POST | `/schedule-blocks` | F-02 | Crear bloque de horario manual | Si |

---

## Scheduling (F-03)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| GET | `/metabolic-windows` | F-03 | Obtener ventanas metabolicas calculadas | Si |
| POST | `/metabolic-windows/recalculate` | F-03 | Forzar recalculo de ventanas | Si |
| GET | `/sleep-targets` | F-03 | Obtener meta de sueno actual | Si |
| PUT | `/sleep-targets` | F-03 | Actualizar meta de sueno | Si |

---

## Glycemic Engine (F-04, F-05, F-06)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| POST | `/food-logs` | F-06 | Registrar comida con items | Si |
| GET | `/food-logs` | F-06 | Listar registros de comida | Si |
| GET | `/food-logs/{id}` | F-06 | Detalle de comida con items | Si |
| POST | `/food-logs/{id}/items` | F-06 | Agregar item a comida existente | Si |
| PATCH | `/food-logs/{id}/order-confirm` | F-06 | Confirmar secuencia de ingesta | Si |
| GET | `/food-logs/{id}/evaluation` | F-04 | Evaluacion del buffer glucemico | Si |
| GET | `/food-logs/{id}/simulation` | F-05 | Datos de simulacion de curva glucemica | Si |

---

## Physical (F-07, F-08)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| GET | `/exercise-triggers/pending` | F-07 | Triggers post-comida pendientes | Si |
| POST | `/exercise-triggers/{id}/complete` | F-07 | Marcar trigger como completado | Si |
| GET | `/strength-plans/current` | F-08 | Plan de fuerza actual del usuario | Si |
| POST | `/strength-plans/generate` | F-08 | Generar nuevo plan de fuerza | Si |
| POST | `/exercise-logs` | F-07, F-08 | Registrar ejercicio completado | Si |
| GET | `/exercise-logs` | F-07, F-08 | Historial de ejercicios | Si |

---

## Profiles y Care Network (F-09, F-10)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| GET | `/profiles/me` | F-09 | Perfil del usuario autenticado | Si |
| PUT | `/profiles/me` | F-09 | Actualizar perfil | Si |
| GET | `/profiles/me/completeness` | F-09 | Porcentaje de completitud del perfil | Si |
| POST | `/pairings` | F-09 | Crear vinculacion paciente-cuidador | Si |
| GET | `/pairings` | F-09 | Listar vinculaciones del usuario | Si |
| PUT | `/pairings/{id}` | F-09 | Actualizar estado o permisos | Si |
| GET | `/pairings/{id}/dashboard` | F-09 | Dashboard del cuidador sobre el paciente | Caregiver |
| GET | `/nudges` | F-10 | Historial de nudges | Si |
| POST | `/nudges/{id}/respond` | F-10 | Cuidador responde al nudge | Caregiver |

---

## Assistant (F-11)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| POST | `/chat/message` | F-11 | Enviar mensaje al asistente | Si |
| GET | `/chat/sessions` | F-11 | Listar sesiones de chat | Si |
| GET | `/chat/sessions/{id}/messages` | F-11 | Historial de mensajes de una sesion | Si |
| POST | `/webhooks/whatsapp` | F-11 | Webhook entrante de WhatsApp | Webhook |
| GET | `/webhooks/whatsapp` | F-11 | Verificacion del webhook de WhatsApp | Webhook |

---

## Reporting (F-12)

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| POST | `/reports/generate` | F-12 | Generar reporte medico para un periodo | Si |
| GET | `/reports` | F-12 | Listar reportes generados | Si |
| GET | `/reports/{id}` | F-12 | Detalle del reporte | Si |
| GET | `/reports/{id}/download` | F-12 | Descargar PDF del reporte | Si |

---

## Risk y ML

| Metodo | Ruta | Feature | Descripcion | Auth |
|--------|------|---------|-------------|------|
| GET | `/risk/current` | ML | Evaluacion de riesgo actual con valores SHAP | Si |
| GET | `/risk/history` | ML | Historial de evaluaciones de riesgo | Si |
| POST | `/risk/evaluate` | ML | Forzar nueva evaluacion de riesgo | Si |

---

## Codigos de Error

| Codigo HTTP | Codigo Interno | Descripcion |
|-------------|---------------|-------------|
| 400 | VALIDATION_ERROR | Datos de entrada invalidos |
| 401 | UNAUTHORIZED | Token ausente o expirado |
| 403 | FORBIDDEN | Sin permisos para el recurso |
| 404 | NOT_FOUND | Recurso no encontrado |
| 409 | CONFLICT | Conflicto de datos (duplicado) |
| 422 | EXTRACTION_FAILED | Fallo en extraccion OCR/LLM |
| 429 | RATE_LIMITED | Limite de solicitudes excedido |
| 500 | INTERNAL_ERROR | Error interno del servidor |
