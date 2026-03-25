# DOCUMENTACION TECNICA - BASE DE DATOS POSTGRESQL NEON

> Version: 1.0.0 | Fecha: 2026-03-25 | Autor: Equipo de Desarrollo

---

## TABLA DE CONTENIDOS

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Problema Identificado](#2-problema-identificado)
3. [Solucion Adoptada](#3-solucion-adoptada)
4. [Configuracion de Neon PostgreSQL](#4-configuracion-de-neon-postgresql)
5. [Estructura de la Base de Datos](#5-estructura-de-la-base-de-datos)
6. [Modelo de Datos Detallado](#6-modelo-de-datos-detallado)
7. [Metodos de Conexion](#7-metodos-de-conexion)
8. [Migracion y Seeds](#8-migracion-y-seeds)
9. [Validaciones Realizadas](#9-validaciones-realizadas)
10. [Seguridad](#10-seguridad)
11. [Limitaciones y Consideraciones](#11-limitaciones-y-consideraciones)
12. [Procedimientos Operativos](#12-procedimientos-operativos)
13. [Resolucion de Problemas](#13-resolucion-de-problemas)
14. [Anexo: Scripts de Utilidad](#14-anexo-scripts-de-utilidad)

---

## 1. RESUMEN EJECUTIVO

### Objetivo
Implementar persistencia de datos real para los entornos QA y Producción de la aplicación ISO 27001 Evaluator, eliminando la pérdida de datos que ocurría con SQLite en el filesystem efímero de Render.

### Decision Tomada
Migrar de SQLite (almacenamiento local) a PostgreSQL en Neon.tech (base de datos administrada en la nube).

### Beneficios Obtenidos
- **Persistencia real**: Los datos no se pierden al reiniciar la instancia
- **Acceso multi-instancia**: QA y Producción comparten la misma base de datos
- **Backups automaticos**: Neon realiza snapshots automáticos
- **Gratuito**: 0.5 GB suficiente para el uso previsto

---

## 2. PROBLEMA IDENTIFICADO

### 2.1 Descripcion del Problema

En el entorno gratuito de Render, las instancias "duermen" después de 15 minutos de inactividad. Cuando la instancia se "despierta", el filesystem se reinicia, causando:

```
+---------------------------+        +---------------------------+
|    Instancia Render       |        |    Filesystem Efimero     |
|    (Free Tier)           |        |    (Se reinicia)         |
+---------------------------+        +---------------------------+
            |                                    |
            v                                    v
    +---------------+                  +--------------------+
    | SQLite DB     |    =======>       |  Base de datos    |
    | iso27001.db   |      RESETEADO    |  VACIA o con      |
    | (en /app)     |                  |  datos iniciales  |
    +---------------+                  +--------------------+
```

### 2.2 Sintomas Observados

| Sintoma | Descripcion |
|---------|-------------|
| Clientes desaparecen | Luego de 15 min sin actividad |
| Usuarios eliminados | Solo quedaban admin@iso27001.local y admin@demo.local |
| Evaluaciones perdidas | Ninguna evaluación persistía |
| Seed se ejecutaba | Cada "despertar" recreaba datos iniciales |

### 2.3 Causa Raiz

El archivo `iso27001.db` estaba almacenado en una ruta dentro del contenedor:
```python
DATABASE_URL = "sqlite:///./iso27001.db"  # Ruta relativa al contenedor
```

Al reiniciar el contenedor, el filesystem vuelve a su estado inicial.

---

## 3. SOLUCION ADOPTADA

### 3.1 Opcion Seleccionada: Neon PostgreSQL

| Criterio | SQLite Local | Neon PostgreSQL | Render Disk |
|----------|--------------|----------------|-------------|
| Persistencia | ❌ No | ✅ Si | ✅ Si |
| Multi-instancia | ❌ No | ✅ Si | ❌ No |
| Backups auto | ❌ No | ✅ Si | ❌ No |
| Costo | $0 | $0 (0.5GB) | $0.10/GB/mes |
| Configuracion | Simple | Media | Media |

### 3.2 Por que Neon y no otra opcion?

| Opcion | Ventajas | Desventajas |
|--------|----------|-------------|
| Neon PostgreSQL | Gratis, gestionado, backups auto | Requiere token de conexion |
| Supabase | Gratis, similar | Menos conocido |
| Render Disk | Rapido | Solo para esa instancia, $0.10/GB |
| ElephantSQL | Gratis | Sin backups automaticos |
| Railway | $5/mes | Costo mensual |

### 3.3 Comparativa de Costos

| Proveedor | Plan | Limite | Precio |
|-----------|------|--------|--------|
| Neon | Free | 0.5 GB | $0 |
| Supabase | Free | 500 MB | $0 |
| Railway | Starter | 1 GB | $5/mes |
| Render Disk | - | 1 GB | $0.10/GB/mes |

**Winner**: Neon - 0.5 GB gratuito, backups automaticos, region Sao Paulo (cercana).

---

## 4. CONFIGURACION DE NEON POSTGRESQL

### 4.1 Datos del Proyecto

| Campo | Valor |
|-------|-------|
| Nombre del Proyecto | ISO27001-QA |
| Region | Sao Paulo (sa-east-1) |
| Proveedor Cloud | AWS |
| Version PostgreSQL | 17 |
| Endpoint Pooler | ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech |

### 4.2 Connection String Completo

```
postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### 4.3 Partes del Connection String

| Parte | Valor | Descripcion |
|-------|-------|-------------|
| Protocolo | postgresql:// | Protocolo de conexion |
| Usuario | neondb_owner | Usuario de la base de datos |
| Password | npg_PhU0gVlXJ5yW | Contraseña (NUNCA compartir) |
| Host | ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech | Endpoint del pooler |
| Puerto | 5432 | Puerto por defecto de PostgreSQL |
| Base de datos | neondb | Nombre de la base de datos |
| Parametros | sslmode=require&channel_binding=require | Seguridad SSL obligatoria |

### 4.4 Configuracion en Render (Environment Variables)

```
Environment Variables en Render Dashboard:

Name:  DATABASE_URL
Value: postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require
```

**Pasos para configurar:**
1. Ir a https://dashboard.render.com
2. Seleccionar servicio (iso27001-qa o iso27001-prod)
3. Environment > Environment Variables
4. Agregar DATABASE_URL
5. Save Changes
6. El servicio se redeploya automaticamente

---

## 5. ESTRUCTURA DE LA BASE DE DATOS

### 5.1 Diagrama de Entidades

```
┌─────────────┐       ┌─────────────┐       ┌──────────────────┐
│   CLIENT    │       │    USER     │       │     NORMA        │
├─────────────┤       ├─────────────┤       ├──────────────────┤
│ id (PK)    │◄──────│ client_id   │       │ id (PK)          │
│ name        │       │ id (PK)     │       │ code             │
│ description │       │ email       │       │ name             │
│ industry    │       │ password    │       │ version          │
│ size        │       │ full_name   │       │ description      │
│ sector      │       │ role        │       │ is_active        │
│ created_at  │       │ is_active   │       │ created_at       │
│ updated_at  │       │ created_at  │       └────────┬─────────┘
└─────────────┘       └──────┬──────┘                │
       │                      │                        │
       │               ┌──────┴──────┐                │
       │               │   SESSION    │                │
       │               ├─────────────┤                │
       │               │ id (PK)     │                │
       │               │ user_id (FK)│                │
       │               │ session_id  │                │
       │               │ expires_at  │                │
       │               └─────────────┘                │
       │                                              │
       │         ┌───────────────────────────────────┴─────┐
       │         │              EVALUATION                       │
       │         ├─────────────────────────────────────────────┤
       │         │ id (PK)                                      │
       │         │ client_id (FK) ──────────► CLIENT           │
       │         │ norma_id (FK)  ──────────► NORMA           │
       │         │ name                                          │
       │         │ description                                   │
       │         │ status                                       │
       │         │ created_by (FK) ─────────► USER             │
       │         │ created_at                                   │
       │         │ updated_at                                   │
       │         │ completed_at                                 │
       │         └─────────────────────┬───────────────────────┘
       │                               │
       │         ┌─────────────────────┴───────────────────────┐
       │         │            CONTROL_RESPONSE                  │
       │         ├─────────────────────────────────────────────┤
       │         │ id (PK)                                      │
       │         │ evaluation_id (FK) ───────► EVALUATION       │
       │         │ control_id (FK) ─────────► CONTROL_DEFINITION│
       │         │ maturity (0-5)                                │
       │         │ not_applicable                                │
       │         │ justification                                 │
       │         │ notes                                         │
       │         │ created_by (FK) ─────────► USER             │
       │         │ created_at                                   │
       │         │ updated_at                                   │
       │         └─────────────────────────────────────────────┘
       │
       │         ┌─────────────────────────────────────────────┐
       └────────►│        CONTROL_DEFINITION                   │
                 ├─────────────────────────────────────────────┤
                 │ id (PK)                                      │
                 │ norma_id (FK) ───────────► NORMA           │
                 │ code                                          │
                 │ domain                                        │
                 │ title                                         │
                 │ description                                   │
                 └─────────────────────────────────────────────┘
```

### 5.2 Tablas Principales

| Tabla | Proposito | Clave Foranea |
|-------|-----------|---------------|
| clients | Empresas/clientes que se auditan | - |
| users | Usuarios del sistema | client_id |
| sessions | Sesiones activas de usuarios | user_id |
| normas | Normas disponibles (ISO 27001, 9001, etc) | - |
| evaluations | Evaluaciones creadas | client_id, norma_id, created_by |
| control_definitions | Definicion de cada control | norma_id |
| control_responses | Respuesta de cada control en cada evaluacion | evaluation_id, control_id |
| audit_logs | Log de todas las acciones | user_id |

### 5.3 Tablas Secundarias

| Tabla | Proposito |
|-------|-----------|
| documents | Documentos cargados |
| document_versions | Versiones de documentos |
| biblioteca_documents | Documentos de la biblioteca |
| rfcs | Requests for Change (ITIL) |
| sprints | Sprints agiles |
| sprint_tasks | Tareas de sprints |

---

## 6. MODELO DE DATOS DETALLADO

### 6.1 Tabla: clients

```sql
CREATE TABLE clients (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    size VARCHAR(50),  -- pequena, mediana, grande
    sector VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Datos de prueba:**
- Cliente Demo (creado por seed)
- Acme Corporation (datos de prueba)
- Global Services S.A. (datos de prueba)

### 6.2 Tabla: users

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- superadmin, admin_cliente, evaluador, vista_solo
    client_id VARCHAR(36),  -- NULL para superadmin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Roles disponibles:**
| Rol | Descripcion | Permisos |
|-----|-------------|----------|
| superadmin | Administrador del sistema | Todo |
| admin_cliente | Admin del cliente | Todo de su cliente |
| evaluador | Puede evaluar controles | Crear/editar evaluaciones |
| vista_solo | Solo lectura | Solo ver, no editar |

**Usuarios por defecto:**
| Email | Password | Rol | Cliente |
|-------|----------|-----|---------|
| admin@iso27001.local | admin123 | superadmin | - |
| admin@demo.local | demo123 | admin_cliente | Cliente Demo |

### 6.3 Tabla: normas

```sql
CREATE TABLE normas (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(20),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Normas disponibles:**
| Code | Name | Version | Controles |
|------|------|---------|-----------|
| ISO27001 | ISO/IEC 27001:2022 | 2022 | 93 |
| ISO9001 | ISO 9001:2015 | 2015 | 25 |
| ISO20000 | ISO/IEC 20000-1:2018 | 2018 | 17 |
| ISO22301 | ISO 22301:2019 | 2019 | 18 |

**Total: 153 controles**

### 6.4 Tabla: evaluations

```sql
CREATE TABLE evaluations (
    id VARCHAR(36) PRIMARY KEY,
    client_id VARCHAR(36) NOT NULL,
    norma_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Estados de evaluacion:**
| Estado | Descripcion |
|--------|-------------|
| draft | Borrador, no iniciada |
| in_progress | En progreso |
| completed | Completada |

### 6.5 Tabla: control_definitions

```sql
CREATE TABLE control_definitions (
    id VARCHAR(36) PRIMARY KEY,
    norma_id VARCHAR(36) NOT NULL,
    code VARCHAR(50) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT
);
```

**Dominios ISO 27001:2022:**
| Dominio | Controles |
|---------|-----------|
| A.5 Controles Organizacionales | 37 |
| A.6 Controles de Personas | 8 |
| A.7 Controles Fisicos | 14 |
| A.8 Controles Tecnologicos | 34 |

### 6.6 Tabla: control_responses

```sql
CREATE TABLE control_responses (
    id VARCHAR(36) PRIMARY KEY,
    evaluation_id VARCHAR(36) NOT NULL,
    control_id VARCHAR(36) NOT NULL,
    maturity INTEGER DEFAULT 0 CHECK (maturity >= 0 AND maturity <= 5),
    not_applicable BOOLEAN DEFAULT FALSE,
    justification TEXT,
    notes TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Niveles de Madurez (CMMI):**
| Nivel | Nombre | Descripcion |
|-------|--------|-------------|
| 0 | No existe | El control no existe |
| 1 | Inicial | Existe pero no se aplica |
| 2 | Gestionado | Se aplica informalmente |
| 3 | Definido | Documentado y aprobado |
| 4 | Cuantitativamente gestionado | Medido y controlado |
| 5 | Optimizado | Mejorado continuamente |

### 6.7 Tabla: audit_logs

```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Acciones registradas:**
| Accion | Descripcion |
|--------|-------------|
| LOGIN | Usuario inicio sesion |
| LOGOUT | Usuario cerro sesion |
| USER_CREATED | Nuevo usuario creado |
| USER_UPDATED | Usuario modificado |
| USER_DELETED | Usuario eliminado |
| CLIENT_CREATED | Nuevo cliente creado |
| EVALUATION_CREATED | Nueva evaluacion creada |
| EVALUATION_STARTED | Evaluacion iniciada |
| EVALUATION_COMPLETED | Evaluacion completada |
| CONTROL_EVALUATED | Control evaluado |
| DOCUMENT_UPLOADED | Documento subido |
| RFC_CREATED | RFC creado |
| RFC_APPROVED | RFC aprobado |

---

## 7. METODOS DE CONEXION

### 7.1 Desde Python (sqlalchemy)

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL, echo=False)
```

### 7.2 Desde Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_PhU0gVlXJ5yW",
    sslmode="require"
)
```

### 7.3 Desde psql (linea de comandos)

```bash
# Instalar psql si no esta (Windows)
# Descargar de: https://www.postgresql.org/download/windows/

# Conectar
psql "host=ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech port=5432 dbname=neondb user=neondb_owner password=npg_PhU0gVlXJ5yW sslmode=require"

# Comandos utiles dentro de psql
\dt          -- Listar tablas
\d clients   -- Describir tabla clients
SELECT * FROM users;  -- Ver usuarios
\q           -- Salir
```

### 7.4 Desde pgAdmin o DBeaver

```
Host: ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech
Port: 5432
Database: neondb
Username: neondb_owner
Password: npg_PhU0gVlXJ5yW
SSL Mode: Require
```

### 7.5 Desde Render (aplicacion)

La aplicacion usa la variable de entorno `DATABASE_URL`. No necesita configuracion adicional.

---

## 8. MIGRACION Y SEEDS

### 8.1 Creacion de Tablas

Las tablas se crean automaticamente al iniciar la aplicacion:

```python
# En app/database.py
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### 8.2 Endpoint de Inicializacion

**URL:** `https://iso27001-qa.onrender.com/admin/debug/init-neon?token=qa-debug-2024`

Este endpoint:
1. Crea todas las tablas si no existen
2. Ejecuta el seed con datos iniciales
3. Verifica la conexion

### 8.3 Datos del Seed

El seed crea:

**Normas:**
- ISO/IEC 27001:2022 (93 controles)
- ISO 9001:2015 (25 controles)
- ISO/IEC 20000-1:2018 (17 controles)
- ISO 22301:2019 (18 controles)

**Usuarios:**
- admin@iso27001.local / admin123 (superadmin)
- admin@demo.local / demo123 (admin_cliente)

**Cliente:**
- Cliente Demo

### 8.4 Verificar Datos Existentes

El seed verifica si ya existen datos antes de crear:

```python
# Si ya existe la norma, no la recrea
existing = session.exec(select(Norma)).first()
if existing:
    return  # Ya existe, omitir

# Si el usuario ya existe, no lo recrea
if not session.exec(select(User).where(User.email == "admin@iso27001.local")).first():
    # Crear usuario
```

---

## 9. VALIDACIONES REALIZADAS

### 9.1 Validaciones de Codigo

| Test | Descripcion | Estado |
|------|-------------|--------|
| test_user_model_exists | Modelo User existe | ✅ PASS |
| test_client_model_exists | Modelo Client existe | ✅ PASS |
| test_evaluation_model_exists | Modelo Evaluation existe | ✅ PASS |
| test_norma_model_exists | Modelo Norma existe | ✅ PASS |
| test_control_definition_has_norma | Control tiene norma_id | ✅ PASS |
| test_control_response_has_na_fields | Response tiene campos N/A | ✅ PASS |
| test_models_import | Modelos se importan | ✅ PASS |
| test_routes_import | Rutas se importan | ✅ PASS |

### 9.2 Validaciones de Autenticacion

| Test | Descripcion | Estado |
|------|-------------|--------|
| test_login_page_loads | Pagina de login carga | ✅ PASS |
| test_login_page_has_csrf_token | Login tiene CSRF | ✅ PASS |
| test_login_success | Login con credenciales validas | ✅ PASS |
| test_login_invalid_credentials | Login con credenciales invalidas | ✅ PASS |
| test_logout_requires_auth | Logout requiere auth | ✅ PASS |

### 9.3 Validaciones de Evaluaciones

| Test | Descripcion | Estado |
|------|-------------|--------|
| test_create_evaluation_form_has_required_fields | Formulario tiene campos | ✅ PASS |
| test_create_evaluation_normas_are_loaded | Normas se cargan | ✅ PASS |
| test_create_evaluation_clients_are_loaded | Clientes se cargan | ✅ PASS |
| test_full_evaluation_creation_flow | Flujo completo de creacion | ✅ PASS |

### 9.4 Validaciones de Admin

| Test | Descripcion | Estado |
|------|-------------|--------|
| test_admin_users_loads_with_superadmin | Admin carga con superadmin | ✅ PASS |
| test_admin_users_has_create_form | Formulario de creacion existe | ✅ PASS |
| test_seed_test_data_endpoint | Seed endpoint funciona | ✅ PASS |
| test_debug_users_with_valid_token | Debug users funciona | ✅ PASS |

**Total: 51 tests pasando**

### 9.5 Validacion de Bug Corregido

**Problema:** `DetachedInstanceError` al crear evaluacion

**Causa:** El objeto `evaluation` se usaba despues de cerrar la sesion

**Solucion:** Guardar `evaluation.id` en una variable antes de cerrar la sesion

```python
# ANTES (INCORRECTO)
session.commit()
return RedirectResponse(url=f"/evaluations/{evaluation.id}")  # Error!

# DESPUES (CORRECTO)
session.flush()
evaluation_id = evaluation.id
# ... mas operaciones ...
session.commit()
return RedirectResponse(url=f"/evaluations/{evaluation_id}")  # OK!
```

---

## 10. SEGURIDAD

### 10.1 SSL/TLS Requerido

La conexion a Neon REQUIERE SSL:

```
sslmode=require
```

Sin SSL, la conexion es rechazada.

### 10.2 Credenciales

| Credencial | Nivel | Ubicacion |
|-----------|-------|----------|
| Password Neon | Critico | Connection string |
| Connection string | Critico | Render Environment Variables |

### 10.3 NO hacer

```bash
# ❌ NUNCA subir a GitHub
git add .
git commit -m "Connection string completo"
git push  # El string estara en el historial!

# ❌ NUNCA compartir
Enviar por email, chat, etc.

# ❌ NUNCA hardcodear en codigo
DATABASE_URL = "postgresql://neondb_owner:password@host..."  # En codigo = MAL
```

### 10.4 SI hacer

```bash
# ✅ Usar variables de entorno
import os
DATABASE_URL = os.environ.get("DATABASE_URL")

# ✅ En .gitignore
.env
*.db
*.sqlite

# ✅ En .env.example (SIN password real)
DATABASE_URL=postgresql://user@host/dbname?sslmode=require
```

### 10.5 Rotacion de Credenciales

Si las credenciales fueron comprometidas:

1. Ir a Neon Dashboard
2. Branches > main > Roles
3. Reset password
4. Copiar nuevo password
5. Actualizar en Render Environment Variables

---

## 11. LIMITACIONES Y CONSIDERACIONES

### 11.1 Limite de Almacenamiento

| Plan | Almacenamiento | Suficiente para |
|------|----------------|-----------------|
| Free | 0.5 GB | 5 clientes, 10 usuarios |

**NO suficiente para:**
- Archivos grandes subidos (>10MB)
- Miles de evaluaciones
- Logs de mas de 1 año

### 11.2 Limite de Conexiones

El free tier de Neon tiene limite de conexiones simultaneas. La aplicacion usa:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
)
```

### 11.3 Region

La base de datos esta en Sao Paulo (sa-east-1). Esto puede afectar la latencia dependiendo de donde esten los usuarios.

---

## 12. PROCEDIMIENTOS OPERATIVOS

### 12.1 Primer Setup (Una vez)

```bash
# 1. Crear cuenta en Neon.tech
# 2. Crear proyecto PostgreSQL
# 3. Obtener connection string
# 4. Configurar DATABASE_URL en Render
# 5. Ejecutar init-neon endpoint
```

### 12.2 Desplegar a QA

```bash
# 1. Hacer cambios en codigo
# 2. Ejecutar tests localmente
python -m pytest tests/ -v

# 3. Commit y push
git add .
git commit -m "feat: descripcion del cambio"
git push origin main

# 4. Esperar deploy automatico en Render (~30 segundos)
# 5. Si hay problemas de datos, ejecutar:
#    https://iso27001-qa.onrender.com/admin/debug/init-neon?token=qa-debug-2024
```

### 12.3 Verificar Persistencia

Despues de hacer cambios, verificar que los datos persisten:

1. Crear un cliente
2. Esperar 15+ minutos (o cerrar el navegador)
3. Volver a la aplicacion
4. Verificar que el cliente sigue existiendo

### 12.4 Backup desde Neon

```bash
# Exportar toda la base de datos
pg_dump -h ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech \
        -U neondb_owner \
        -d neondb \
        -F c \
        -f iso27001_backup.dump

# Restaurar
pg_restore -h ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech \
           -U neondb_owner \
           -d neondb \
           iso27001_backup.dump
```

---

## 13. RESOLUCION DE PROBLEMAS

### 13.1 Error: "connection refused"

**Causa:** Endpoint incorrecto o firewall bloqueando

**Solucion:**
- Verificar que el endpoint sea correcto
- Verificar sslmode=require

### 13.2 Error: "too many connections"

**Causa:** Muchas conexiones simultaneas

**Solucion:**
- Reducir pool_size en database.py
- Reiniciar la aplicacion

### 13.3 Error: "database does not exist"

**Causa:** Base de datos no existe

**Solucion:**
- Crear base de datos en Neon Dashboard
- O ejecutar init-neon endpoint

### 13.4 Error: "SSL required"

**Causa:** Falta el parametro sslmode

**Solucion:**
- Agregar ?sslmode=require al connection string

### 13.5 Error: "password authentication failed"

**Causa:** Password incorrecto

**Solucion:**
- Reset password en Neon Dashboard
- Actualizar connection string

### 13.6 Error 500 al crear evaluacion

**Causa:** Base de datos vacia

**Solucion:**
- Ejecutar: `https://iso27001-qa.onrender.com/admin/debug/init-neon?token=qa-debug-2024`

---

## 14. ANEXO: SCRIPTS DE UTILIDAD

### 14.1 Script: init_neon_db.py

Ubicacion: `scripts/init_neon_db.py`

```python
#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL en Neon.
Uso: python scripts/init_neon_db.py
"""
import os
from sqlmodel import create_engine, SQLModel
from app.models import *  # Todos los modelos

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"
)

def main():
    print(f"Conectando a Neon PostgreSQL...")
    engine = create_engine(DATABASE_URL, echo=True)
    print("Creando tablas...")
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas exitosamente!")

if __name__ == "__main__":
    main()
```

### 14.2 Verificar Tablas

```python
from sqlalchemy import inspect

def verificar_tablas():
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    print("Tablas en la base de datos:")
    for tabla in tablas:
        print(f"  - {tabla}")
```

### 14.3 Contar Registros

```python
from sqlmodel import Session, select
from app.models import User, Client, Norma

def contar_registros():
    with Session(engine) as session:
        usuarios = session.exec(select(User)).all()
        clientes = session.exec(select(Client)).all()
        normas = session.exec(select(Norma)).all()
        
        print(f"Usuarios: {len(usuarios)}")
        print(f"Clientes: {len(clientes)}")
        print(f"Normas: {len(normas)}")
```

---

## HISTORIAL DE CAMBIOS

| Version | Fecha | Descripcion | Autor |
|---------|-------|-------------|-------|
| 1.0.0 | 2026-03-25 | Creacion inicial del documento | Equipo de Desarrollo |

---

## REFERENCIAS

| Recurso | URL |
|---------|-----|
| Neon Dashboard | https://console.neon.tech |
| Documentacion Neon | https://neon.tech/docs |
| Pricing Neon | https://neon.tech/pricing |
| Render Dashboard | https://dashboard.render.com |
| Render Docs | https://render.com/docs |

---

*Documento creado para referencia del equipo de desarrollo. Mantener actualizado ante cualquier cambio en la configuracion.*
