# ROADMAP - Plan de Implementacion de Funcionalidades

> Version: 1.1.0 | Fecha: 2026-03-24

---

## Estado Actual

**ISO 27001 Evaluator v1.3.0** esta funcionando con:
- 4 normas ISO (27001, 9001, 20000-1, 22301)
- 153 controles en total
- Evaluaciones, evidencias, biblioteca
- Dashboard, estadisticas, import/export
- N/A con justificacion
- Multi-tenant, roles (incl VISTA_SOLO), auditlog

---

## Funcionalidades Implementadas

### FASE 1: Mejoras Inmediatas (COMPLETADO)

| # | Modulo | Descripcion | Estado | Version |
|---|--------|-------------|--------|---------|
| 1.1 | N/A con Justificacion | Opcion N/A en madurez con campo de justificacion | COMPLETADO | v1.2.0 |
| 1.2 | Recalculo de Score | Excluir N/A del denominador | COMPLETADO | v1.2.0 |
| 1.3 | Indicador de progreso | % de evaluacion en lista | COMPLETADO | v1.2.0 |

### FASE 2: Multi-Norma (COMPLETADO)

| # | Modulo | Descripcion | Estado | Version |
|---|--------|-------------|--------|---------|
| 2.1 | Selector de Norma | Elegir ISO 27001, 9001, 20000-1, 22301 | COMPLETADO | v1.3.0 |
| 2.2 | Controles ISO 9001:2015 | 25 clausulas | COMPLETADO | v1.3.0 |
| 2.3 | Controles ISO 20000-1 | 17 controles | COMPLETADO | v1.3.0 |
| 2.4 | Controles ISO 22301 | 18 controles | COMPLETADO | v1.3.0 |

### FASE 3: Modulos Avanzados

| # | Modulo | Descripcion | Estado |
|---|--------|-------------|--------|
| 3.1 | Catalogo de Servicios | CRUD servicios + SLAs | PENDIENTE |
| 3.2 | BIA | Analisis de Impacto al Negocio | PENDIENTE |
| 3.3 | SoA Automatizada | Declaracion de Aplicabilidad | PENDIENTE |
| 3.4 | No Conformidades | Registro y seguimiento de NCs | PENDIENTE |
| 3.5 | Mapa de Procesos | Diagrama visual de procesos | PENDIENTE |
| 3.6 | DAFO/PESTEL | Analisis de contexto | PENDIENTE |
| 3.2 | BIA | Analisis de Impacto al Negocio | PENDIENTE |
| 3.3 | SoA Automatizada | Declaracion de Aplicabilidad | PENDIENTE |
| 3.4 | No Conformidades | Registro y seguimiento de NCs | PENDIENTE |
| 3.5 | Mapa de Procesos | Diagrama visual de procesos | PENDIENTE |
| 3.6 | DAFO/PESTEL | Analisis de contexto | PENDIENTE |

### FASE 4: Mejoras de UX/UI

| # | Modulo | Descripcion | Estado |
|---|--------|-------------|--------|
| 4.1 | Dashboard Ejecutivo | Resumen para direccion | PENDIENTE |
| 4.2 | Reportes PDF | Generar reportes | PENDIENTE |
| 4.3 | Notificaciones | Alertas de vencimiento | PENDIENTE |
| 4.4 | Dashboard del Cliente | Vista limitada por cliente | PENDIENTE |

---

## Detalle Tecnico

### N/A con Justificacion

**Objetivo:** Permitir marcar un control como "No Aplica" con justificacion.

**Cambios requeridos:**
1. Modificar modelo `ControlResponse` - agregar campo `justification`
2. Modificar template de evaluacion - agregar opcion N/A + campo justificacion
3. Modificar calculo de score - excluir N/A del denominador

### Multi-Norma

**Objetivo:** Soportar ISO 9001, 20000-1, 22301 ademas de 27001.

**Cambios requeridos:**
1. Agregar tabla `Norma` (id, nombre, version, descripcion)
2. Modificar `ControlDefinition` - agregar campo `norma_id`
3. Modificar `Evaluation` - agregar campo `norma_id`
4. Crear seeds para cada norma

### Catalogo de Servicios (ISO 20000)

**Objetivo:** Gestionar servicios y sus SLAs.

**Modelo:**
```
Servicio:
  - id
  - client_id
  - nombre
  - descripcion
  - tipo (interno/externo)
  - estado (activo/inactivo)

SLA:
  - id
  - servicio_id
  - nombre
  - metricas
  - objetivo (%)
  - peso

Incidente:
  - id
  - servicio_id
  - descripcion
  - fecha_inicio
  - fecha_resolucion
  - estado
```

### BIA (ISO 22301)

**Objetivo:** Analisis de Impacto al Negocio.

**Modelo:**
```
ProcesoNegocio:
  - id
  - client_id
  - nombre
  - descripcion
  - rto (Recovery Time Objective)
  - rpo (Recovery Point Objective)
  - impacto (critico/alto/medio/bajo)

Activo:
  - id
  - proceso_id
  - nombre
  - tipo
  - ubicacion
```

### No Conformidades

**Objetivo:** Registrar y seguir NCs.

**Modelo:**
```
NoConformidad:
  - id
  - evaluation_id
  - control_id (nullable)
  - tipo (mayor/menor/observacion)
  - descripcion
  - causa_raiz
  - accion_correctiva
  - responsable_id
  - fecha_limite
  - estado (abierta/cerrada)
  - evidencia_cierre
```

---

## Orden de Implementacion Sugerido

1. **N/A con justificacion** - Mejora inmediata de usabilidad
2. **Selector de Norma** - Base para multi-norma
3. **Controles ISO 9001** - Siguiente norma mas comun
4. **Catalogo de Servicios** - Valor agregado para ITIL
5. **No Conformidades** - Completa el ciclo de evaluacion
6. **BIA** - Para ISO 22301

---

## Recursos Requeridos

- **Desarrollador(es):** 1-2
- **Tiempo estimado FASE 1:** 1-2 dias
- **Tiempo estimado FASE 2:** 1-2 semanas
- **Tiempo estimado FASE 3:** 2-4 semanas
- **Tiempo estimado FASE 4:** 2-3 semanas

---

*Roadmap vivo - se actualiza segun avance del proyecto.*
