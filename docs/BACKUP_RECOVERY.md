# PROCEDIMIENTOS DE BACKUP Y RECUPERACION - ISO 27001 Evaluador

> Version: 1.0.0 | Fecha: 2026-03-23

---

## 1. ALCANCE Y OBJETIVO

Este documento establece los procedimientos de respaldo (backup) y recuperacion para el sistema ISO 27001 Evaluator, cubriendo:

- **Codigo fuente**: Repositorio GitHub + archivos locales
- **Base de datos**: PostgreSQL (Neon.tech) - evaluaciones, usuarios, configuraciones
- **Archivos**: Evidencias cargadas por usuarios (uploads)
- **Documentacion**: Todos los archivos MD del proyecto

**Objetivo:** Garantizar la disponibilidad e integridad de los datos del sistema ISO 27001 Evaluator, permitiendo recuperacion ante desastres, errores humanos o fallos tecnicos.

---

## 2. UBICACIONES DE DESARROLLO Y RESPALDO

### 2.1 Estructura de trabajo

| Nivel | Ubicacion | Descripcion |
|-------|------------|--------------|
| **DESARROLLO (Activo)** | `F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad` | Carpeta de trabajo principal donde se desarrolla |
| **DESARROLLO (Respaldo)** | `C:\Users\vpalma\Documents\Desarrollo\OpenCode_Antigravity\ISO27001_ITIL_seguridad` | Punto de respaldo local PC |
| **GITHub** | `https://github.com/VPR65/iso27001-evaluator` | Control de versiones |
| **QA** | `https://iso27001-qa.onrender.com` | Entorno de pruebas |
| **PRODUCCION** | `https://iso27001-prod.onrender.com` | Entorno de produccion |

### 2.2 Directorios de respaldo en F:

```
F:\Desarrollo\Opencode\
├── ISO27001_ITIL_seguridad\     ← DESARROLLO ACTIVO
│   ├── app\
│   ├── docs\
│   ├── scripts\
│   ├── iso27001.db            ← Base de datos activa
│   └── ...
│
└── iso27001-backup\            ← RESPALDOS
    ├── codigo\
    │   ├── 20260323_iso27001-evaluator_v1.1.0.zip
    │   ├── 20260324_iso27001-evaluator_v1.2.0.zip
    │   └── ...
    ├── database\
    │   ├── iso27001_20260323.db.backup
    │   ├── iso27001_20260324.db.backup
    │   └── ...
    ├── docs\
    │   ├── docs_20260323.zip
    │   └── ...
    └── uploads\
        ├── uploads_20260323.zip
        └── ...
```

---

## 3. FLUJO DE TRABAJO CON PUNTOS DE RESPALDO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE DESARROLLO                                 │
│                    (Con multiples puntos de respaldo)                    │
└─────────────────────────────────────────────────────────────────────────────┘

    F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad (DESARROLLO ACTIVO)
                            │
                            │ 1. Trabajar en codigo
                            │    uvicorn app.main:app --reload
                            │
                            ▼
    ┌───────────────────────────────────────────────────────────┐
    │ 2. PUNTO DE RESPALDO ANTES DE CAMBIOS IMPORTANTES         │
    │    - Comprimir a F:\...\iso27001-backup\codigo\          │
    │    - Backup DB a F:\...\iso27001-backup\database\        │
    └───────────────────────────────────────────────────────────┘
                            │
                            │ 3. Git commit + push
                            ▼
    GitHub (VPR65/iso27001-evaluator)
                            │
                            │ 4. Desplegar a QA (Render)
                            ▼
    https://iso27001-qa.onrender.com (QA)
                            │
                            │ 5. Aprobar en QA
                            ▼
    https://iso27001-prod.onrender.com (PRODUCCION)
```

---

## 4. FRECUENCIA DE RESPALDOS

| Tipo de backup | Frecuencia | Retention | Responsable |
|----------------|------------|-----------|--------------|
| **Completo** (codigo + DB + uploads) | Antes de cada cambio importante | 12 semanas | Desarrollador |
| **Base de datos** | Diario o antes de cada despliegue | 30 dias | Desarrollador |
| **Codigo Git** | Cada commit significativo | Indefinido (Git) | Desarrollador |
| **Snapshot F:** | Antes de cada merge a main | 8 versiones | Desarrollador |
| **Pre-despliegue a prod** | Antes de cada release | 4 versiones | Desarrollador |

---

## 5. PROCEDIMIENTO DE BACKUP

### 5.1 Backup completo a unidad F:

```cmd
REM === ISO 27001 Evaluator - BACKUP COMPLETO ===

REM 1. Ir a carpeta de desarrollo en F:
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

REM 2. Verificar que el codigo compila
python -c "from app.main import app; print('OK')"

REM 3. Fecha para nombre de archivo
set FECHA=%date:~-4,4%%date:~-7,2%%date:~-10,2%

REM 4. Backup de base de datos
copy iso27001.db "F:\Desarrollo\Opencode\iso27001-backup\database\iso27001_%FECHA%.db.backup"

REM 5. Comprimir codigo fuente
powershell -Command "Compress-Archive -Path 'app','docs','scripts','*.py','*.md','*.txt','Dockerfile','docker-compose.yml' -DestinationPath 'F:\Desarrollo\Opencode\iso27001-backup\codigo\codigo_%FECHA%_v1.1.0.zip' -Force"

REM 6. Verificar integridad
dir "F:\Desarrollo\Opencode\iso27001-backup"

echo Backup completado exitosamente!
pause
```

### 5.2 Backup mediante script automatizado

```bash
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

# Backup completo (DB + uploads)
python scripts/backup.py backup

# Backup solo base de datos
python scripts/backup.py backup-db

# Listar backups disponibles
python scripts/backup.py list
```

### 5.3 Checklist pre-backup

- [ ] Verificar que no hay procesos de la app en ejecucion
- [ ] Verificar que la app compila sin errores (`python -c "from app.main import app"`)
- [ ] Confirmar que hay espacio suficiente en disco F:
- [ ] Documentar el backup en el registro (fecha, version, notas)
- [ ] Verificar que los archivos sensibles (.env) no se incluyen

---

## 6. PROCEDIMIENTO DE RECUPERACION

### 6.1 Recuperacion desde F: (Desarrollo)

```cmd
REM 1. Detener el servidor si esta corriendo
REM (Ctrl+C en la terminal de uvicorn)

REM 2. Ir al directorio de desarrollo F:
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

REM 3. Listar backups disponibles
dir "F:\Desarrollo\Opencode\iso27001-backup\database"

REM 4. Copiar base de datos desde backup
copy "F:\Desarrollo\Opencode\iso27001-backup\database\iso27001_20260323.db.backup" iso27001.db

REM 5. Si hay corrupcion de codigo, extraer desde ZIP
powershell -Command "Expand-Archive -Path 'F:\Desarrollo\Opencode\iso27001-backup\codigo\codigo_20260323.zip' -DestinationPath 'F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad' -Force"

REM 6. Verificar que la app inicia correctamente
uvicorn app.main:app --reload --port 8000
```

### 6.2 Recuperacion desde GitHub

```bash
# Si el codigo local se corrompio, restaurar desde GitHub
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
git fetch origin
git reset --hard origin/main

# Si necesitas restaurar una version especifica
git checkout v1.0.0
```

---

## 7. PROCEDIMIENTO DE ROLLBACK (VOLVER A VERSION ANTERIOR)

### 7.1 Rollback de codigo

```bash
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

# Ver versiones disponibles
python scripts/rollback.py --list

# Rollback al tag anterior (hace backup automatico primero)
python scripts/rollback.py

# Rollback a version especifica
python scripts/rollback.py v1.0.0
```

### 7.2 Rollback manual desde F:

```cmd
REM Buscar version anterior en F:
dir F:\Desarrollo\Opencode\iso27001-backup\codigo

REM Extraer version deseada
powershell -Command "Expand-Archive -Path 'F:\Desarrollo\Opencode\iso27001-backup\codigo\codigo_20260320.zip' -DestinationPath 'F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad' -Force"
```

---

## 8. VERIFICACION POST-RECUPERACION

| Verificacion | Accion | Esperado |
|--------------|--------|----------|
| App inicia | `python -c "from app.main import app; print('OK')"` | `OK` |
| Health endpoint | `curl http://localhost:8000/health` | `{"status":"ok"}` |
| Login funciona | Acceder a `/login` | Formulario visible |
| Dashboard carga | Acceder a `/dashboard` | KPIs visibles |
| Base de datos | Verificar usuarios | `admin@iso27001.local` existe |
| Controles ISO | Verificar 93 controles | Contar = 93 |

---

## 9. PUNTOS DE RESPALDO - NOMENCLATURA

| Tipo | Formato nombre | Ejemplo |
|------|----------------|----------|
| Codigo | `codigo_AAAAMMDD_vX.X.X.zip` | `codigo_20260323_v1.1.0.zip` |
| Database | `iso27001_AAAAMMDD.db.backup` | `iso27001_20260323.db.backup` |
| Docs | `docs_AAAAMMDD.zip` | `docs_20260323.zip` |
| Uploads | `uploads_AAAAMMDD.zip` | `uploads_20260323.zip` |

---

## 10. RESPONSABILIDADES

| Rol | Responsabilidad |
|-----|------------------|
| Desarrollador | Ejecutar backups programados, verificar integridad, documentar incidentes |
| Change Manager | Aprobar restores en prod, verificar impacto |
| Project Sponsor | Autorizar recuperaciones mayores |

---

## 11. MATRIZ DE RECUPERACION

| Escenario | Tiempo objetivo | Procedimiento | Responsable |
|-----------|------------------|----------------|--------------|
| DB corrupta desarrollo | < 30 min | Restore desde backup F: | Desarrollador |
| DB corrupta produccion | < 1 hora | Restore desde backup + verificar | Desarrollador + Change Manager |
| Codigo perdido en F: | < 15 min | Git checkout o extraer ZIP F: | Desarrollador |
| PC fallo completo | < 4 horas | Reclonar desde GitHub a F: | Desarrollador |
| Desastre mayor | < 24 horas | Reconstruir desde cero usando docs | Equipo completo |

---

## 12. REGISTRO DE BACKUPS

| Fecha | Tipo | Ubicacion destino | Version | Realizado por | Notas |
|-------|------|-------------------|---------|---------------|-------|
| 2026-03-23 | Completo | F:\...\iso27001-backup\ | v1.1.0 | Desarrollador | Backup inicial |
| | | | | | |

*Este registro se debe actualizar cada vez que se ejecute un backup.*

---

## 13. ANEXO: COMANDOS RAPIDOS

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"

REM === BACKUP ===
python scripts/backup.py backup
python scripts/backup.py backup-db
python scripts/backup.py list

REM === ROLLBACK ===
python scripts/rollback.py --list
python scripts/rollback.py
python scripts/rollback.py v1.1.0

REM === COPIAR A BACKUP F: ===
copy iso27001.db "F:\Desarrollo\Opencode\iso27001-backup\database\iso27001_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db.backup"

powershell -Command "Compress-Archive -Path 'app','docs','scripts','*.py','*.md' -DestinationPath 'F:\Desarrollo\Opencode\iso27001-backup\codigo\codigo_%date:~-4,4%%date:~-7,2%%date:~-10,2%_v1.1.0.zip' -Force"
```

---

*Documento creado siguiendo estandares ITIL. Actualizar en cada version del sistema.*