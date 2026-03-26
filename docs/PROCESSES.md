# PROCESOS DE DESARROLLO - ISO 27001 Evaluator

> Version: 1.1.2 | Ultima actualizacion: 2026-03-23

---

## INDICE

1. [Proceso de Desarrollo](#1-proceso-de-desarrollo)
2. [Proceso de Cambios (RFC)](#2-proceso-de-cambios-rfc)
3. [Proceso de Incidentes](#3-proceso-de-incidentes)
4. [Proceso de Backup y Recuperacion](#4-proceso-de-backup-y-recuperacion)
5. [Proceso de Despliegue](#5-proceso-de-despliegue)
6. [Proceso de Gestion de Configuracion](#6-proceso-de-gestion-de-configuracion)
7. [Proceso de Mejora Continua (Retrospectivas)](#7-proceso-de-mejora-continua-retrospectivas)

---

## 1. PROCESO DE DESARROLLO

### 1.1 Flujo de Trabajo (Git Flow)

```
┌─────────────────────────────────────────────────────────┐
│  main (produccion)                                      │
│    └─ merge solo desde dev (release tags)               │
│                                                         │
│  dev (integracion)                                      │
│    └─ merge desde feature/*                            │
│                                                         │
│  feature/nombre (desarrollo)                            │
│    └─ merge a dev cuando esta listo                   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Pasos para desarrollar una nueva funcionalidad

```bash
# 1. Crear rama desde dev
git checkout dev
git pull origin dev
git checkout -b feature/mi-nueva-funcionalidad

# 2. Trabajar en la funcionalidad
# ... escribir codigo ...

# 3. Commit con prefijo correcto
git add .
git commit -m "feat: agregar nueva funcionalidad"

# 4. Subir rama
git push -u origin feature/mi-nueva-funcionalidad

# 5. Crear Pull Request en GitHub/GitLab

# 6. Merge a dev (despues de review)
git checkout dev
git merge feature/mi-nueva-funcionalidad
git push origin dev

# 7. Eliminar rama feature
git branch -d feature/mi-nueva-funcionalidad
```

### 1.3 Prefijos de Commits

| Prefijo      | Uso                                         |
|--------------|---------------------------------------------|
| `feat:`     | Nueva funcionalidad                         |
| `fix:`       | Correccion de bug                           |
| `security:`  | Correccion de vulnerabilidad               |
| `refactor:`  | Mejora de codigo sin cambiar funcionalidad  |
| `docs:`      | Documentacion                               |
| `backup:`    | Restauracion de datos                       |
| `config:`    | Cambios de configuracion                    |
| `deps:`      | Actualizacion de dependencias              |

### 1.4 Criterios para hacer Commit

- [ ] Codigo compila sin errores
- [ ] No hay secretos hardcodeados (usar variables de entorno)
- [ ] Inputs de usuario sanitizados
- [ ] Backup creado antes de migrar DB (si aplica)
- [ ] Mensaje de commit con prefijo correcto
- [ ] Prueba basica realizada

---

## 2. PROCESO DE CAMBIOS (RFC)

Todo cambio significativo en el codigo debe pasar por el proceso de RFC.

### 2.1 Tipos de Cambio

| Tipo        | Descripcion                                     | Ejemplo                        |
|-------------|------------------------------------------------|--------------------------------|
| Correctivo  | Correccion de un defecto                        | Fix de bug en login            |
| Adaptativo  | Cambio por requisito nuevo                       | Agregar nuevo rol de usuario    |
| Perfectivo  | Mejora de rendimiento o mantenibilidad           | Refactorizar consulta SQL       |
| Preventivo  | Evitar futuros problemas                        | Agregar validacion de input    |

### 2.2 Niveles de Riesgo

| Nivel   | Descripcion                                  | Tiempo de implementacion |
|---------|----------------------------------------------|--------------------------|
| P1 Critico | Sistema caido, fuga de datos, corrupcion     | Inmediato (< 1 hora)     |
| P2 Alto   | Funcionalidad critica afectada               | < 24 horas               |
| P3 Medio  | Funcionalidad parcial afectada               | < 1 semana               |
| P4 Bajo   | Cambios menores, cosmeticos                 | < 2 semanas              |

### 2.3 Flujo de Aprobacion

```
Solicitud RFC
    │
    ▼
Clasificacion (tipo + nivel de riesgo)
    │
    ▼
Evaluacion de impacto
    │
    ├── P4/P3 ──► Dev Lead revisa ──► Aprueba ──► Implementa
    │                                                │
    │                                                ▼
    │                                         Prueba (QA)
    │                                                │
    │                                                ▼
    │                                         Merge a dev
    │
    └── P1/P2 ──► Change Manager + Dev Lead ──► Aprueba
                                                  │
                                                  ▼
                                            Implementa en rama de emergencia
                                                  │
                                                  ▼
                                            Prueba + Despliegue urgente
                                                  │
                                                  ▼
                                            Documenta en el RFC
```

### 2.4 Crear un RFC en el Sistema

1. Ir a `/rfcs/new`
2. Llenar:
   - **Titulo**: descripcion breve del cambio
   - **Descripcion**: justificacion, impacto, alternativas consideradas
   - **Tipo de cambio**: Correctivo / Adaptativo / Perfectivo / Preventivo
   - **Nivel de riesgo**: P1-P4
   - **Esfuerzo estimado**: horas/dias
3. El sistema calcula automaticamente el nivel de riesgo ponderado
4. Esperar aprobacion segun el flujo

### 2.5 Cerrar un RFC

- Marcar como completado en el sistema
- Incluir hash del commit que implementa el cambio
- Documentar lecciones aprendidas (si hubo alguna)
- El audit log registra automaticamente el cierre

---

## 3. PROCESO DE INCIDENTES

### 3.1 Clasificacion de Incidentes

| Prioridad | Descripcion                        | SLA de respuesta |
|-----------|------------------------------------|-------------------|
| P1        | Sistema no disponible               | 15 minutos        |
| P2        | Funcionalidad critica afectada      | 1 hora            |
| P3        | Funcionalidad no critica afectada  | 4 horas           |
| P4        | Inconveniente menor                | 24 horas          |

### 3.2 Flujo de Respuesta

```
Incidente detectado
    │
    ▼
Registrar en sistema (RFC tipo "Correctivo")
    │
    ▼
Responder segun SLA
    │
    ├── P1/P2 ──► Llamada telefonica a Dev Lead + Team
    │               Reunion inmediata
    │
    └── P3/P4 ──► Ticket en sistema
                    Notificacion por chat/email
    │
    ▼
Diagnostico (15 min max)
    │
    ▼
Solucion provisional (workaround)
    │
    ▼
Solucion definitiva
    │
    ▼
Verificacion
    │
    ▼
Cierre del incidente
    │
    ▼
Revision post-incidente (solo P1/P2)
    - Causa raiz
    - Que se hizo
    - Acciones preventivas
```

### 3.3 Acciones Inmediatas (P1)

```bash
# 1. Notificar al equipo inmediatamente
# 2. Evaluar alcance con:
python -c "from app.main import app; print('App OK')"

# 3. Si la DB esta corrupta, restaurar desde backup:
python scripts/backup.py restore backups/backup_ULTIMO.zip

# 4. Si hay vulnerabilidad, cambiar secrets inmediatamente:
#    - SECRET_KEY
#    - passwords en .env
#    - tokens de API

# 5. Documentar todo en el RFC de incidente
```

---

## 4. PROCESO DE BACKUP Y RECUPERACION

### 4.1 Tipos de Backup

| Tipo        | Contenido                        | Frecuencia  | Retencion |
|-------------|----------------------------------|-------------|-----------|
| Completo    | DB + uploads                    | Diario (auto) | 7 dias    |
| Base de datos | Solo DB PostgreSQL                  | Cada cambio  | 30 dias   |
| Semanal     | DB + uploads                    | Semanal     | 4 semanas |
| Manual       | Antes de cada despliegue          | A demanda   | Indefinida |

### 4.2 Comandos de Backup

```bash
# Backup completo (DB + uploads)
python scripts/backup.py backup

# Backup solo base de datos
python scripts/backup.py backup-db

# Listar backups disponibles
python scripts/backup.py list

# Restaurar desde backup
python scripts/backup.py restore backups/backup_YYYYMMDD.zip

# Rollback de codigo a version anterior
python scripts/rollback.py                  # al tag anterior
python scripts/rollback.py v1.0.0           # a version especifica
python scripts/rollback.py --list           # ver todos los tags
```

### 4.3 Plan de Recuperacion ante Desastres (DRP)

#### Escenario 1: Base de datos corrupta
```bash
# 1. Detener el servicio
# 2. Identificar el backup mas reciente
python scripts/backup.py list

# 3. Restaurar desde backup
python scripts/backup.py restore backups/backup_20260322.zip

# 4. Verificar que la app funciona
curl http://localhost:8000/health

# 5. Reiniciar servicio
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# 6. Documentar el incidente en el sistema RFC
```

#### Escenario 2: Codigo da�ado (necesita rollback)
```bash
# 1. Verificar que el rollback no pierde datos de la DB
# 2. Listar tags disponibles
python scripts/rollback.py --list

# 3. Ejecutar rollback
python scripts/rollback.py v1.0.0

# 4. El script hace backup automatico antes de rollback
# 5. Verificar que la app inicia
uvicorn app.main:app --reload

# 6. Si el rollback es de DB, restaurar el backup generado
```

#### Escenario 3: Servidor comprometido
```bash
# 1. Aislar el servidor (cortar red)
# 2. Cambiar TODOS los secretos inmediatamente
#    - SECRET_KEY
#    - Passwords de DB
#    - Tokens de API

# 3. Restaurar desde backup limpio
python scripts/backup.py restore backups/backup_FECHA.zip

# 4. Verificar integridad
# 5. Cambiar puertos y configuraciones de red
# 6. Monitorear accesos por 72 horas
```

### 4.4 Checklist de Verificacion Post-Backup

- [ ] El archivo .zip se creo correctamente
- [ ] El tamano del archivo es razonable (> 1KB)
- [ ] La DB se puede abrir con sqlite3
- [ ] Los archivos de uploads estan incluidos
- [ ] Se registro en el audit log

---

## 5. PROCESO DE DESPLIEGUE

### 5.1 Checklist Pre-Despliegue

- [ ] Backup completo creado (`python scripts/backup.py backup`)
- [ ] Tests basicos pasaron
- [ ] Codigo compila sin errores (`python -c "from app.main import app; print('OK')"`)
- [ ] Health check pasa (`curl http://localhost:8000/health`)
- [ ] Nueva version taggeada (vX.Y.Z)
- [ ] Documentacion actualizada (CHANGELOG.md)
- [ ] Stakeholders notificados (si es release grande)

### 5.2 Pasos de Despliegue (Flujo QA -> Prod)

```
rama main (QA)  ──────────────────►  iso27001-qa.onrender.com
     │
     │ git merge (despues de QA OK)
     ▼
rama production ──────────────────►  iso27001-prod.onrender.com
```

```bash
# 1. CREAR BACKUP pre-despliegue
python scripts/backup.py backup

# 2. DESARROLLAR en rama main
git checkout main
# ... hacer cambios, commitear ...
git push origin main
# --> QA se actualiza automaticamente

# 3. PROBAR en QA
#    https://iso27001-qa.onrender.com
#    Verificar todo funciona OK

# 4. SI QA OK -> MERGE a production
git checkout production
git merge main
git push origin production
# --> PROD se actualiza automaticamente

# 5. VERIFICAR en PROD
#    https://iso27001-prod.onrender.com
curl https://iso27001-prod.onrender.com/health

# 6. TAGGEAR version en production
git checkout production
git tag v1.2.0 -m "Release v1.2.0"
git push origin production --tags
```

### 5.2b Ramas Git

| Rama | Uso | Auto-deploy |
|------|-----|-------------|
| `main` | Desarrollo y QA | Render QA: iso27001-qa |
| `production` | Produccion estable | Render Prod: iso27001-prod |

### 5.2c Cambiar rama en Render

Si necesitas cambiar la rama de un servicio en Render:
1. Ve a Render Dashboard -> tu servicio
2. Settings -> Branches
3. Cambiar la rama -> Save changes

### 5.3 Rollback (1 comando, < 30 segundos)

```bash
# Rollback al tag anterior
python scripts/rollback.py

# Rollback a version especifica
python scripts/rollback.py v1.0.0

# Ver todos los tags
python scripts/rollback.py --list
```

### 5.4 Checklist Post-Despliegue

- [ ] Health check responde 200
- [ ] Login funciona
- [ ] Modulos principales accesibles
- [ ] No hay errores 500 en consola
- [ ] Registro en CHANGELOG.md actualizado

---

## 6. PROCESO DE GESTION DE CONFIGURACION

### 6.1 Versionado Semantico (Semver)

```
vMAJOR.MINOR.PATCH

  MAJOR: Cambio incompatible en API o arquitectura
  MINOR: Nueva funcionalidad compatible hacia atras
  PATCH: Correccion de bugs compatible hacia atras
```

| Tipo de cambio        | Ejemplo                           | Incremento |
|----------------------|------------------------------------|------------|
| Nuevo control ISO       | Agregar modulo de reportes PDF     | MINOR      |
| Nuevo endpoint API      | Endpoint /api/v2/estadisticas     | MINOR      |
| Fix de bug             | Corregir paginacion en listado     | PATCH      |
| Refactor de BD         | Cambiar estructura de una tabla     | MAJOR      |
| Nuevo rol de usuario    | Agregar rol "Auditor"             | MINOR      |
| Cambio de endpoint      | /old -> /api/v2/new                | MAJOR      |

### 6.2 Versionado de Documentos (Interno)

Los documentos dentro del sistema usan versionado semantico:

```
v1.0.0 - Inicial (draft)
v1.1.0 - En revision
v1.2.0 - Aprobado
v1.3.0 - Published
```

- Cada nueva version recibe un numero secuencial
- Se puede hacer diff entre versiones
- Se puede hacer rollback a version anterior

### 6.3 Archivos de Configuracion

| Archivo          | Descripcion                     | En git? |
|------------------|----------------------------------|---------|
| `.env`           | Secrets, passwords, keys         | NO      |
| `.env.example`  | Template de variables de entorno  | SI      |
| `app/config.py`  | Configuracion de la app          | SI      |
| `requirements.txt` | Dependencias Python             | SI      |
| `docker-compose.yml` | Configuracion Docker         | SI      |

**NUNCA hacer commit de archivos con secretos.**

---

## 7. PROCESO DE MEJORA CONTINUA (RETROSPECTIVAS)

### 7.1 Frecuencia

- **Sprint Retrospective**: Cada sprint (2 semanas)
- **Release Retrospective**: Cada release (vX.Y.Z)
- **Post-Incident Review**: Despues de cada incidente P1/P2

### 7.2 Formato de Retrospectiva

```
# Retrospectiva Sprint #X - [Fecha]

## Lo que funciono bien
-

## Que se puede mejorar
-

## Acciones para el proximo sprint
-

## Incidentes/S problemas
-

## Completado del sprint anterior
-

## Compromisos del equipo
-
```

### 7.3 MetricAS DE SEGUIMIENTO

| Metrica                          | Objetivo    | Actual  |
|----------------------------------|-------------|---------|
| Tiempo de resolucion de incidentes P1 | < 1 hora   | -       |
| Tiempo de resolucion de incidentes P2 | < 24 horas | -       |
| Controles ISO evaluados por sprint  | > 10        | -       |
| Cobertura de tests automatizados    | > 50%       | 0%      |
| Uptime del sistema               | > 99.5%      | -       |
| Tiempo de despliegue             | < 15 min    | < 5 min |
