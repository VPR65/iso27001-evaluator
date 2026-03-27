# DEFINICION DEL PROYECTO - ISO 27001 & ITIL Evaluator

**Version:** 2.0.0  
**Fecha:** 27 de Marzo de 2026  
**Estado:** En Produccion (v1.7.1)  
**Ultima Revision:** 2026-03-27  

---

## Control de Versiones del Documento

| Version | Fecha | Autor | Cambios Principales |
|---------|-------|-------|---------------------|
| 1.0.0 | 2026-03-22 | Equipo Desarrollo | Documento inicial |
| 1.1.0 | 2026-03-23 | Equipo Desarrollo | Agrega multi-norma (ISO 9001, 20000, 22301) |
| 1.2.0 | 2026-03-24 | Equipo Desarrollo | Agrega ITIL v4 y panel admin |
| 1.3.0 | 2026-03-25 | Equipo Desarrollo | Agrega Sprint 1 (evaluacion avanzada) |
| 1.4.0 | 2026-03-26 | Equipo Desarrollo | Agrega Sprint 2 (reportes y dashboard) |
| 1.4.1 | 2026-03-26 | Equipo Desarrollo | Correccion documentacion SQLite -> PostgreSQL |
| **2.0.0** | **2026-03-27** | **Equipo Desarrollo** | **Arquitectura Hibrida Multi-Modo + Sprint 3** |

---

## 1. Vision Ejecutiva del Proyecto

### 1.1 Proposito
Sistema web multi-tenant para evaluar el cumplimiento de controles de seguridad bajo normas **ISO 27001:2022** e **ITIL v4**, con capacidad de operar en **4 modos de despliegue** para adaptarse a diferentes requisitos de soberania de datos y costos.

### 1.2 Los 4 Ejercicios Completados

#### Ejercicio 1: Cimentacion (v1.0.0 - v1.3.0)
- Arquitectura FastAPI + PostgreSQL
- Multi-norma (5 normas, 187 controles)
- Multi-tenant (5 clientes, 10 usuarios)
- Autenticacion y roles
- **Costo:** $0/mes (Render Free + Neon Free)

#### Ejercicio 2: Modulo de Evaluacion Avanzada (v1.5.0)
- Carga multiple de evidencias
- Historial de cambios (audit trail)
- Plantillas de respuestas predefinidas
- **Costo:** $0/mes

#### Ejercicio 3: Reportes y Dashboard (v1.6.0)
- Dashboard de cumplimiento por cliente
- Comparativa de evaluaciones
- Exportacion avanzada a Excel
- **Costo:** $0/mes

#### Ejercicio 4: Seguridad y Soberania (v1.7.1)
- Autenticacion 2FA (TOTP)
- Auditoria de logs detallada
- Encriptacion de evidencias
- Soporte Ollama local
- Multi-modo (cloud/hibrido/on-premise)
- **Costo:** $0/mes

---

## 2. Arquitectura Hibrida Multi-Modo

### 2.1 Los 4 Modos de Operacion

| Modo | Nombre | DB | Archivos | IA | Cliente Ideal | Costo |
|------|--------|-----|----------|-----|---------------|-------|
| **1** | **Cloud Demo** | Neon.tech | Render Disk | NVIDIA NIM | Testing, Demo | $0 |
| **2** | **Cloud Seguro** | Neon.tech | S3/MinIO | Oracle Ollama | Enterprise cloud | $0 |
| **3** | **Hibrido** | Oracle VM | Oracle VM | Oracle Ollama | Enterprise soberania | $0 |
| **4** | **On-Premise** | PostgreSQL Local | NAS/SMB | Ollama Local | Banca, Gobierno | Hardware |

### 2.2 Matriz de Decision por Modo

| Componente | Modo 1: Cloud Demo | Modo 2: Cloud Seguro | Modo 3: Hibrido | Modo 4: On-Premise |
|------------|--------------------|---------------------|-----------------|-------------------|
| **DB** | Neon.tech Free | Neon.tech | Oracle PostgreSQL | PostgreSQL Local |
| **Storage** | Render Disk (1GB) | S3/MinIO | Oracle VM (200GB) | NAS/SMB Local |
| **IA** | NVIDIA NIM | Oracle Ollama | Oracle Ollama | Ollama Local |
| **App** | Render Free | Render Free | Oracle VM | Docker Local |
| **2FA** | SI | SI | SI | SI |
| **Encriptacion** | Opcional | Recomendado | Obligatorio | Obligatorio |
| **Auditoria** | Logs basicos | Logs completos | Logs completos | Logs completos |
| **Costo** | $0/mes | $0/mes | $0/mes | Hardware ($500-2000) |
| **ISO-Compliant** | Parcial | SI | SI | SI |
| **Soberania** | Baja | Alta | Total | Total |

---

## 3. Configuracion por Modo

### 3.1 Modo 1: Cloud Demo (Testing/Demo)

**Archivo:** `.env.cloud_demo`

```bash
DEPLOY_MODE=cloud
DATABASE_URL=postgresql://user:pass@neon.tech/db
AI_MODE=nvidia
NVIDIA_API_KEY=tu_api_key
```

**Caracteristicas:**
- Costo: $0/mes
- Deploy en 5 minutos
- Ideal para demos y testing
- IA externa (NVIDIA)
- Storage efimero
- No ISO-compliant para produccion

---

### 3.2 Modo 2: Cloud Seguro (Enterprise con Soberania)

**Archivo:** `.env.cloud_secure`

```bash
DEPLOY_MODE=hybrid
DATABASE_URL=postgresql://user:pass@rds.amazonaws.com/db
AI_MODE=ollama
AI_LOCAL_URL=https://tu-oracle-cloud.com:11434
AI_LOCAL_MODEL=llama3.2
```

**Caracteristicas:**
- Costo: $0/mes (Oracle Free Tier)
- IA soberana (en tu control)
- Storage persistente (S3)
- ISO-compliant
- Requiere configurar Oracle Cloud (2 horas)

---

### 3.3 Modo 3: Hibrido (Oracle Cloud Full)

**Archivo:** `.env.hybrid_oracle`

```bash
DEPLOY_MODE=onpremise
DATABASE_URL=postgresql://postgres:pass@localhost:5432/iso27001
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.2
```

**Caracteristicas:**
- Costo: $0/mes (Oracle Free Tier)
- Todo en un solo lugar (VM)
- Maxima soberania
- ISO-compliant total
- Requiere Oracle Cloud setup

---

### 3.4 Modo 4: On-Premise (Servidor del Cliente)

**Archivo:** `.env.onpremise`

```bash
DEPLOY_MODE=onpremise
DATABASE_URL=postgresql://postgres:pass@localhost:5432/iso27001
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.2
```

**Caracteristicas:**
- Costo: Hardware del cliente ($500-2000 unico)
- Maxima seguridad
- Air-gap possible
- ISO 27001 full compliant
- Requiere hardware y mantenimiento

---

## 4. Guia de Implementacion por Ejercicio

### Ejercicio 1: Cimentacion (Completado)
**Completado:**
- FastAPI + PostgreSQL (Neon)
- 5 normas (ISO 27001, 9001, 20000, 22301, ITIL v4)
- 187 controles
- Multi-tenant
- Auth con roles
- 70 tests automatizados
- Deploy en Render Free

---

### Ejercicio 2: Evaluacion Avanzada (Completado)
**Completado:**
- Carga multiple de evidencias
- Historial de cambios (audit trail)
- Plantillas de respuestas
- Drag & drop de archivos
- Vista previa de archivos

**Endpoints Clave:**
- POST /evaluate/{id}/control/{ctrl}/upload - Subir evidencia
- GET /evaluate/{id}/control/{ctrl}/history - Ver historial
- GET /templates - Gestionar plantillas

---

### Ejercicio 3: Reportes y Dashboard (Completado)
**Completado:**
- Dashboard de cumplimiento por cliente
- Comparativa de evaluaciones
- Exportacion a Excel avanzado
- Graficos con Chart.js
- KPIs visuales

**Endpoints Clave:**
- GET /reports/compliance/{client_id} - Dashboard
- GET /reports/comparison - Comparativa
- GET /export/excel/{evaluation_id} - Exportar Excel

---

### Ejercicio 4: Seguridad y Soberania (Completado)
**Completado:**
- Autenticacion 2FA (TOTP)
- Auditoria de logs detallada
- Encriptacion de evidencias
- Soporte Ollama local
- Multi-modo (cloud/hybrid/onpremise)

**Endpoints Clave:**
- GET /auth/2fa/setup - Configurar 2FA
- GET /audit/logs - Ver auditoria
- POST /evaluate/{id}/control/{ctrl}/upload - Sube encriptado

---

## 5. Comparativa de Escenarios

### 5.1 Para Demo / Testing
| Concepto | Solucion | Costo | Tiempo Setup |
|----------|----------|-------|--------------|
| App Web | Render Free | $0 | 10 min |
| DB | Neon.tech Free | $0 | 5 min |
| Storage | Render Disk | $0 | 0 min |
| IA | NVIDIA NIM | $0 | 15 min |
| **TOTAL** | | **$0/mes** | **30 min** |

**Ventajas:**
- Rapido de deployar
- Sin configuracion
- Ideal para mostrar a clientes

**Desventajas:**
- IA externa (no soberana)
- Storage efimero
- No ISO-compliant para produccion

---

### 5.2 Para Enterprise Cloud (Recomendado)
| Concepto | Solucion | Costo | Tiempo Setup |
|----------|----------|-------|--------------|
| App Web | Render Free | $0 | 10 min |
| DB | Neon.tech Free | $0 | 5 min |
| Storage | Oracle VM (200GB) | $0 | 30 min |
| IA | Oracle Ollama | $0 | 30 min |
| **TOTAL** | | **$0/mes** | **1.25 horas** |

**Ventajas:**
- Soberania de datos (IA local)
- Storage persistente
- ISO-compliant
- Costo cero

**Desventajas:**
- Requiere Oracle Cloud setup
- Configurar firewall

---

### 5.3 Para On-Premise (Banca/Gobierno)
| Concepto | Solucion | Costo | Tiempo Setup |
|----------|----------|-------|--------------|
| Servidor | Hardware local | $500-2000 | 1 vez |
| App + DB + IA | Docker Stack | $0 | 1 hora |
| Mantenimiento | Cliente | Variable | Continuo |
| **TOTAL** | | **$500-2000** | **2 horas** |

**Ventajas:**
- Control total
- Air-gap possible
- Maxima seguridad
- ISO 27001 fu
