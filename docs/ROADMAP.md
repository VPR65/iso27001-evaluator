# ROADMAP - ISO 27001 & ITIL Evaluator

**Última actualización:** 2026-03-30
**Versión Actual:** v1.8.3
**Estado:** ✅ Producción - Monitoreo y Alertas Implementados

---

## 📋 Resumen Ejecutivo

### ✅ Fases Completadas (100%)

| Fase | Versión | Estado | Descripción |
|------|---------|--------|-------------|
| **Fase 1: Cimentación** | v1.0.0 - v1.3.0 | ✅ 100% | Arquitectura base, multi-norma, auth |
| **Fase 2: Evaluación Avanzada** | v1.5.0 | ✅ 100% | Carga múltiple, audit trail, plantillas |
| **Fase 3: Reportes** | v1.6.0 | ✅ 100% | Dashboard, comparativa, Excel |
| **Fase 4: Seguridad** | v1.7.0 | ✅ 100% | 2FA, auditoría, encriptación |
| **Fase 5: IA On-Demand** | v1.7.4 | ✅ 100% | IA local Ollama, fallback automático |
| **Fase 6: Documentación** | v1.7.4 | ✅ 100% | 28 docs, scripts, guías |
| **Fase 7: Despliegue y Automatización** | v1.8.1 | ✅ 100% | Docker, scripts deploy, auto-backups |
| **Fase 8: Monitoreo y Alertas** | v1.8.3 | ✅ 100% | Monitor sistema, alertas, health checks |

**Progreso Total:** 98% del proyecto completado

---

## 🎯 PRÓXIMOS PASOS (Fase 7 - En Desarrollo)

### 7. Despliegue y Automatización

**Prioridad:** ALTA  
**Timeline:** Q2 2026  
**Archivos:** `docker-compose.yml`, `scripts/deploy/`

#### 7.1 Docker Compose para On-Premise
- [ ] Crear `docker-compose.yml` con: App + DB + Ollama
- [ ] Configurar volúmenes persistentes
- [ ] Variables de ambiente pre-configuradas
- [ ] Scripts de inicio/parada automática
- [ ] Soporte para Oracle Cloud Free Tier

#### 7.2 Scripts de Instalación Automática
- [ ] Script de instalación para Windows
- [ ] Script de instalación para Linux/Mac
- [ ] Detección automática de dependencias
- [ ] Configuración guiada (wizard)
- [ ] Backup/restore automático

#### 7.3 Backups Automáticos
- [ ] Agendar backups diarios
- [ ] Rotación de backups (7 días)
- [ ] Backup a S3/MinIO
- [ ] Verificación automática de backups
- [ ] Alertas por email si falla backup

---

### 8. Mejoras de IA (Opcional)

**Prioridad:** MEDIA  
**Timeline:** Q3 2026

#### 8.1 Modelos Adicionales de Ollama
- [ ] Soporte para múltiples modelos simultáneos
- [ ] Auto-descarga de modelos bajo demanda
- [ ] Gestión de espacio en disco
- [ ] Modelos recomendados por tipo de control

#### 8.2 Mejoras en Análisis de IA
- [ ] Análisis de contexto cruzado entre controles
- [ ] Detección de inconsistencias
- [ ] Sugerencias basadas en histórico
- [ ] Integración con RAG (Retrieval-Augmented Generation)

---

### 9. Multi-Tenancy Avanzado

**Prioridad:** MEDIA  
**Timeline:** Q3 2026

#### 9.1 Panel Multi-Cliente
- [ ] Dashboard unificado para múltiples clientes
- [ ] Switching entre clientes sin logout
- [ ] Plantillas compartidas entre clientes
- [ ] Reportes consolidados

#### 9.2 Colaboración en Tiempo Real
- [ ] Múltiples evaluadores en misma evaluación
- [ ] Chat integrado por control
- [ ] Historial de cambios colaborativo
- [ ] Notificaciones push

---

## 📊 HISTORIAL DE VERSIONES

### v1.7.4 - 2026-03-30 ✅ ACTUAL
- ✅ Sistema de IA on-demand con fallback automático
- ✅ Detección de Ollama con polling (5 seg)
- ✅ Indicadores visuales (🟢/🟡/🔴)
- ✅ Scripts Start/Stop Ollama
- ✅ Documentación completa (28 docs)
- ✅ Modelos: qwen3.5:0.8b, phi3:mini, phi:latest, llama3.1:latest, qwen2:7b

### v1.7.3 - 2026-03-27 ✅
- ✅ Selector de modelos en GUI
- ✅ Soporte multi-proveedor (NVIDIA + Ollama)
- ✅ Endpoints: GET /api/ai/models, POST /api/ai/set-model

### v1.7.2 - 2026-03-27 ✅
- ✅ Encriptación de evidencias
- ✅ Auditoría de logs

### v1.7.1 - 2026-03-27 ✅
- ✅ 2FA TOTP implementado
- ✅ Soporte Ollama local

### v1.7.0 - 2026-03-27 ✅
- ✅ Multi-modo (cloud/hybrid/on-premise)
- ✅ PROJECT_DEFINITION.md creado

### v1.6.0 - 2026-03-26 ✅
- ✅ Dashboard de cumplimiento por cliente
- ✅ Comparativa de evaluaciones
- ✅ Exportación avanzada a Excel

### v1.5.0 - 2026-03-26 ✅
- ✅ Carga múltiple de evidencias
- ✅ Historial de cambios (audit trail)
- ✅ Plantillas de respuestas predefinidas

### v1.4.1 - 2026-03-26 ✅
- ✅ ITIL v4 framework
- ✅ Panel admin completo

### v1.3.0 - 2026-03-25 ✅
- ✅ Multi-norma (5 normas, 187 controles)
- ✅ 70+ tests automatizados

---

## 📅 CRONOLOGÍA ACTUALIZADA

| Fecha | Hito | Versión | Estado |
|-------|------|---------|--------|
| 2026-03-22 | Inicio del proyecto | v1.0.0 | ✅ Completado |
| 2026-03-24 | Multi-norma implementada | v1.3.0 | ✅ Completado |
| 2026-03-26 | Sprint 1-3 completados | v1.6.0 | ✅ Completado |
| 2026-03-27 | IA On-Demand implementada | v1.7.4 | ✅ Completado |
| 2026-03-30 | Documentación 100% | v1.7.4 | ✅ Completado |
| 2026-04-15 | Docker Compose | v1.8.0 | 📅 Pendiente |
| 2026-04-30 | Scripts automatización | v1.8.1 | 📅 Pendiente |
| 2026-05-15 | Backups automáticos | v1.8.2 | 📅 Pendiente |

---

## 🎯 MÉTRICAS ACTUALES

### Código
- **Líneas de código:** ~16,000
- **Endpoints:** 50+
- **Modelos DB:** 15+
- **Tests:** 70+ (85% cobertura)

### Documentación
- **Documentos:** 28 archivos
- **Scripts:** 9 archivos
- **Páginas de doc:** ~500+

### IA
- **Modelos soportados:** 5 (Ollama) + múltiples (NVIDIA)
- **Modos:** Local (Ollama) → Cloud (NVIDIA) → None
- **Polling:** 5 segundos
- **Cache:** 5 segundos

### Despliegue
- **Modos soportados:** 4 (Cloud Demo, Cloud Seguro, Híbrido, On-Premise)
- **Costo:** $0/mes (Oracle Free Tier + Neon Free)
- **Backups:** Manuales (automatización pendiente)

---

## ⚠️ RIESGOS ACTIVOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Oracle cambie términos free tier | Baja | Alto | Backup en Google Cloud Free |
| Ollama consuma mucha RAM | Media | Medio | Modelos ligeros (3B-7B) |
| Cliente sin skills técnicos | Media | Alto | Documentación clara + scripts |
| Render cambie free tier | Baja | Medio | Backup Railway/HF Spaces |
| Brecha seguridad | Baja | Crítico | Encriptación + 2FA + Auditoría |

---

## 📝 CONTROL DE CAMBIOS DEL ROADMAP

| Fecha | Versión | Cambio |
|-------|---------|--------|
| 2026-03-22 | v1.0 | Documento inicial creado |
| 2026-03-24 | v1.1 | Reestructuración completa |
| 2026-03-26 | v1.2 | Agregados sprints 1-3 |
| 2026-03-27 | v1.3 | Agregado sprint 4 (IA) |
| 2026-03-30 | v2.0 | **Actualización mayor** - Reflejado v1.7.4 real, fases completadas, próximos pasos claros |

---

> **Nota:** Este documento se actualizó completamente el 2026-03-30 para reflejar el estado real del proyecto (v1.7.4). Las próximas actualizaciones se realizarán al finalizar cada sprint o cuando cambien las prioridades.

**Próxima revisión:** 2026-04-15  
**Responsable:** Equipo de Desarrollo  
**Estado:** ✅ Aprobado
