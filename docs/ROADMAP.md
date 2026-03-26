# ROADMAP - ISO 27001 Evaluator

**Última actualización:** 2026-03-26  
**Versión Actual:** v1.4.1

---

## 📋 Estado Actual (v1.4.1)

### ✅ Completado
- [x] Arquitectura FastAPI + PostgreSQL (Neon.tech)
- [x] Multi-norma: ISO 27001:2022 (93 controles), ITIL v4 (34 prácticas), ISO 9001, 20000, 22301
- [x] Panel Admin completo (clientes, usuarios, evaluaciones)
- [x] Barra de progreso visual en evaluaciones
- [x] Dashboard con explicación del Score de Madurez
- [x] Validación automática de documentación
- [x] 70+ tests automatizados
- [x] Deploy QA/Prod en Render.com
- [x] Integración NVIDIA NIM (código base, sin API Key configurada)

---

## 🎯 PRIORIDAD ALTA (En Desarrollo - Sprint Actual)

Estas funcionalidades están en curso y son el foco del desarrollo activo.

### 3. Módulo de Evaluación Avanzada
**Estado:** 🔄 En desarrollo  
**Archivos:** `app/routes/evaluations.py`, `app/templates/evaluate/`

#### 3.1 Carga Múltiple de Evidencias
- [ ] Permitir subir 3+ archivos por control
- [ ] Previsualización de archivos adjuntos
- [ ] Eliminar evidencias individuales
- [ ] Soportar: PDF, DOCX, XLSX, PNG, JPG

#### 3.2 Historial de Cambios (Auditoría)
- [ ] Log de cada modificación en respuestas
- [ ] Mostrar versión anterior y nueva
- [ ] Timestamp y usuario que modificó
- [ ] Vista de "quién cambió qué y cuándo"

#### 3.3 Plantillas de Respuestas Predefinidas
- [ ] Crear biblioteca de respuestas estándar
- [ ] Aplicar plantilla a múltiples controles
- [ ] Personalizar plantillas por cliente
- [ ] Ejemplos: "Política documentada", "Sin evidencia", "Parcial"

---

### 4. Módulo de Reportes y Dashboard Avanzado
**Estado:** 🔄 En desarrollo  
**Archivos:** `app/routes/stats.py`, `app/templates/stats/`

#### 4.1 Dashboard de Cumplimiento por Cliente
- [ ] Score por norma (ISO 27001, ITIL v4, etc.)
- [ ] Comparativa entre períodos
- [ ] Top 5 controles más críticos
- [ ] Gráfico de radar por dominios

#### 4.2 Comparativa de Evaluaciones
- [ ] Seleccionar 2+ evaluaciones de misma norma
- [ ] Ver progreso/retroceso por control
- [ ] Gráfico de líneas de evolución
- [ ] Exportar comparativa a PDF

#### 4.3 Exportación Avanzada a Excel
- [ ] Reporte ejecutivo con logo de empresa
- [ ] Múltiples pestañas (resumen, por dominio, hallazgos)
- [ ] Gráficos incrustados
- [ ] Formato profesional con colores

---

### 5. Mejoras de Seguridad
**Estado:** 🔄 En desarrollo  
**Archivos:** `app/auth.py`, `app/models.py`, `app/security.py`

#### 5.1 Autenticación en Dos Factores (2FA)
- [ ] Soporte para TOTP (Google Authenticator)
- [ ] Códigos de recuperación
- [ ] Habilitar/deshabilitar por usuario
- [ ] Forzar 2FA para roles admin

#### 5.2 Auditoría de Logs de Acceso
- [ ] Registrar cada login (exitoso/fallido)
- [ ] IP de origen, navegador, hora
- [ ] Alerta por múltiples intentos fallidos
- [ ] Vista de "actividad reciente" para usuarios

#### 5.3 Encriptación de Evidencias
- [ ] Encriptar archivos subidos (AES-256)
- [ ] Desencriptar solo al visualizar
- [ ] Clave por cliente
- [ ] Backup de claves en vault

---

### 6. Integración ITIL v4 Avanzada
**Estado:** 🔄 En desarrollo  
**Archivos:** `app/routes/itil.py`, `app/templates/itil/`

#### 6.1 Vincular ISO con ITIL
- [ ] Mapeo automático: Control ISO → Práctica ITIL
- [ ] Ejemplo: A.5.8 (Gestión de proyectos) → Change Enablement
- [ ] Sugerir prácticas ITIL para controles no conformes

#### 6.2 Generar RFCs desde Hallazgos
- [ ] Detectar controles no conformes
- [ ] Crear RFC borrador automáticamente
- [ ] Sugerir prioridad basada en impacto
- [ ] Vincular RFC con evaluación original

#### 6.3 Dashboard de Prácticas ITIL
- [ ] Evaluar madurez de 34 prácticas
- [ ] Comparar con benchmark ISO 27001
- [ ] Identificar brechas de gobernanza
- [ ] Reporte de alineación ISO-ITIL

---

## 📦 PENDIENTES (Backlog - Futuro)

Estas funcionalidades quedan postergadas pero documentadas para retomar en sprints futuros.

### 1. Activar IA con NVIDIA NIM
**Estado:** ⏸️ Pendiente - Requiere API Key  
**Archivos:** `app/ai_service.py`, `app/routes/ai_routes.py`

#### Tareas Pendientes:
- [ ] Configurar variable `NVIDIA_API_KEY` en Render (QA y Prod)
- [ ] Habilitar endpoint `/api/ai/analyze-control` en UI
- [ ] Crear componente HTMX para análisis en tiempo real
- [ ] Mostrar sugerencias de IA en vista de evaluación
- [ ] Botón "Generar recomendaciones con IA"
- [ ] Exportar resumen ejecutivo generado por IA

**Dependencias:**
- API Key de NVIDIA (gestión segura)
- Testing con datos reales
- Validar costo/uso de API

---

### 2. Mejoras en Panel de Administración
**Estado:** ⏸️ Pendiente  
**Archivos:** `app/routes/admin.py`, `app/templates/admin/`

#### 2.1 Estadísticas Avanzadas
- [ ] Gráfico de tendencia temporal
- [ ] Top usuarios que más evalúan
- [ ] Tiempo promedio por evaluación
- [ ] Controles más fallados (ranking)

#### 2.2 Gestión Masiva de Usuarios
- [ ] Importar desde Excel/CSV
- [ ] Asignar rol por defecto
- [ ] Notificar credenciales por email
- [ ] Baja masiva (soft delete)

#### 2.3 Reporte de Auditoría
- [ ] Listar todos los logs de los últimos 30 días
- [ ] Filtrar por usuario, acción, fecha
- [ ] Exportar logs a CSV
- [ ] Alertas de actividad sospechosa

---

### 3. Funcionalidades de Evaluación (Backlog Secundario)
**Estado:** ⏸️ Pendiente

#### 3.1 Evaluación Colaborativa
- [ ] Múltiples usuarios en misma evaluación
- [ ] Asignar controles por usuario
- [ ] Comentarios en cada control
- [ ] Notificaciones de cambios

#### 3.2 Plantillas de Evaluación
- [ ] Crear evaluación desde plantilla
- [ ] Personalizar preguntas por cliente
- [ ] Versión de plantillas
- [ ] Compartir plantillas entre clientes

#### 3.3 Recordatorios Automáticos
- [ ] Configurar fecha de vencimiento
- [ ] Email recordatorio 7 días antes
- [ ] Notificar evaluaciones incompletas
- [ ] Reporte de estado semanal

---

## 📊 Planificación por Sprints

### Sprint 1 (Actual) - v1.5.0
**Enfoque:** Módulo de Evaluación Avanzada
- Carga múltiple de evidencias
- Historial de cambios
- Plantillas de respuesta

### Sprint 2 - v1.6.0
**Enfoque:** Reportes y Dashboard
- Dashboard de cumplimiento
- Comparativa de evaluaciones
- Exportación Excel avanzada

### Sprint 3 - v1.7.0
**Enfoque:** Seguridad
- 2FA (TOTP)
- Auditoría de logs
- Encriptación de evidencias

### Sprint 4 - v1.8.0
**Enfoque:** Integración ITIL v4
- Mapeo ISO-ITIL
- Generación de RFCs
- Dashboard ITIL

### Sprint 5 - v2.0.0
**Enfoque:** IA y Automatización
- Activar NVIDIA NIM
- Análisis automático
- Recomendaciones inteligentes

---

## 📝 Control de Cambios del Roadmap

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 2026-03-24 | v1.0 | Documento inicial creado |
| 2026-03-26 | v1.1 | Reestructuración completa: prioridades 3-6 activas, 1-2 en backlog |

---

> **Nota:** Este documento es dinámico y debe actualizarse al finalizar cada sprint o cuando cambien las prioridades del proyecto.
