# RFC-0001: Soporte Multi-Norma (ISO 27001, 9001, 20000-1, 22301)

## Informacion General

| Campo | Valor |
|-------|-------|
| RFC ID | RFC-0001 |
| Fecha de creacion | 2026-03-24 |
| Solicitante | Equipo de Desarrollo |
| Estado | Completado |
| Version | v1.3.0 |
| Commit | 44182f2 |

## Descripcion del Cambio

Implementar soporte para multiples normas ISO en el sistema de evaluacion, permitiendo evaluar organizaciones contra ISO 27001, ISO 9001, ISO 20000-1 e ISO 22301.

## Justificacion

Segun el documento "Guia Estrategica para el Desarrollo de la Herramienta Integral de Evaluacion ISO", el sistema debe soportar multiples normas del Anexo SL para crear un Sistema de Gestion Integrado (IMS).

## Cambios Tecnicos

### Modelo de Datos
- Nueva entidad Norma para representar cada norma ISO
- Campo norma_id agregado a Evaluation y ControlDefinition
- Seeds actualizados con controles de las 4 normas

### Controles por Norma
- ISO 27001:2022 (ISO27001) - Seguridad de la Informacion - 93 controles
- ISO 9001:2015 (ISO9001) - Gestion de la Calidad - 25 clausulas
- ISO 20000-1:2018 (ISO20000) - Gestion de Servicios TI - 17 controles
- ISO 22301:2019 (ISO22301) - Continuidad del Negocio - 18 controles

## Tipo de Cambio
Adaptativo - Nueva funcionalidad requerida por el negocio

## Nivel de Riesgo
P3 Medio - Funcionalidad parcial afectada

## Impacto
- Base de datos requiere recreacion (nuevos campos)
- Todas las evaluaciones existentes mantienen ISO 27001
- No hay perdida de datos

## Rollback
- Version anterior: v1.2.0
- Tag: git checkout v1.2.0
- Backup: backups/backup_full_20260324_151315.zip

## Prueba de Aceptacion
- [ ] Crear evaluacion con ISO 27001
- [ ] Crear evaluacion con ISO 9001
- [ ] Crear evaluacion con ISO 20000-1
- [ ] Crear evaluacion con ISO 22301
- [ ] Verificar que solo se muestran controles de la norma seleccionada
- [ ] Verificar calculo de score por norma
- [ ] Verificar exportacion de Excel

## Aprobacion

| Rol | Fecha | Estado |
|-----|-------|--------|
| Dev Lead | 2026-03-24 | Completado |
| Change Manager | Pendiente | Pendiente |

## Notas de Cierre

Implementado en commit 44182f2. Tag v1.3.0 creado. QA deploy automatizado desde rama main.
