# MANUAL DE ACCESO A PLATAFORMAS - ISO 27001 Evaluator

> Version: 1.0.0 | Fecha: 2026-03-24

---

## 1. RENDER.COM (QA y Produccion)

### 1.1 Acceso al Dashboard

1. Ir a: https://dashboard.render.com
2. Login con: **vpalma05@hotmail.com**
3. Usar login via **GitHub**

### 1.2 Ver Logs de un Servicio

1. Seleccionar el servicio (iso27001-qa o iso27001-prod)
2. Click en tab **"Logs"**
3. Ver logs en tiempo real

### 1.3 Trigger Deploy Manual

1. Ir a servicio
2. Click en **"Manual Deploy"**
3. Seleccionar **"Deploy latest commit"**

### 1.4 Reiniciar Servicio

1. Ir a servicio
2. Click en **"Manual Deploy"**
3. Click en **"Clear build cache & deploy"**

### 1.5 Acceder a Variables de Entorno

1. Ir a servicio
2. Menu izquierdo: **"Environment"**
3. Ver todas las variables configuradas

### 1.6 Acceder a la Base de Datos (Limitado en Free Tier)

**Importante:** El plan gratuito de Render NO permite acceso directo a PostgreSQL/SQLite.

**Alternativas:**
- Usar el endpoint `/admin/debug/users` en la app
- Exportar datos via la funcionalidad de export
- Conectar via Render CLI (requiere plan pago)

---

## 2. GITHUB

### 2.1 Repositorio

**URL:** https://github.com/VPR65/iso27001-evaluator

### 2.2 Acceso

1. Ir a la URL del repositorio
2. Login con: **vpalma05@hotmail.com**

### 2.3 Ver Commits

1. Ir a: https://github.com/VPR65/iso27001-evaluator/commits/main

### 2.4 Ver Tags

1. Ir a: https://github.com/VPR65/iso27001-evaluator/tags

### 2.5 Ver Releases

1. Ir a: https://github.com/VPR65/iso27001-evaluator/releases

### 2.6Descargar Codigo de una Version

1. Ir a **Tags**
2. Click en el tag (ej: v1.3.0)
3. Click en **"Download ZIP"**

---

## 3. ACCESO LOCAL (Desarrollo)

### 3.1 Carpeta del Proyecto

```
F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad
```

### 3.2 Base de Datos Local

```
F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad\iso27001.db
```

### 3.3 Verificar Codigo

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
python -c "from app.main import app; print('OK')"
```

### 3.4 Iniciar Servidor Local

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3.5 Verificar Base de Datos

```cmd
python -c "
from app.database import engine
from sqlmodel import Session, select
from app.models import User

with Session(engine) as s:
    users = s.exec(select(User)).all()
    for u in users:
        print(f'{u.email} - {u.role.value}')
"
```

---

## 4. BACKUPS LOCALES

### 4.1 Carpeta de Backups

```
F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad\backups\
```

### 4.2 Ver Backups Disponibles

```cmd
dir backups
```

### 4.3 Crear Backup Manual

```cmd
python scripts/backup.py backup
```

### 4.4 Restaurar desde Backup

```cmd
python scripts/backup.py restore backups\backup_full_YYYYMMDD_HHMMSS.zip
```

---

## 5. RUTAS DE LA APLICACION (Debug)

### 5.1 Ver Usuarios (JSON)

URL: `/admin/debug/users`

### 5.2 Ver Audit Logs (JSON)

URL: `/admin/debug/audit-logs`

---

## 6. CREDENCIALES DE ACCESO

### 6.1 Aplicacion

| Entorno | URL | Usuario | Password |
|---------|-----|---------|----------|
| Desarrollo | http://localhost:8000 | admin@iso27001.local | admin123 |
| QA | https://iso27001-qa.onrender.com | admin@iso27001.local | admin123 |
| Produccion | https://iso27001-prod.onrender.com | admin@iso27001.local | admin123 |

### 6.2 Plataformas

| Servicio | Cuenta | Metodo de Login |
|----------|--------|----------------|
| Render | vpalma05@hotmail.com | GitHub |
| GitHub | vpalma05@hotmail.com | Browser |

---

## 7. RESOLUCION DE PROBLEMAS

### 7.1 QA no responde

1. Ir a dashboard.render.com
2. Seleccionar servicio iso27001-qa
3. Ver Logs para identificar error
4. Trigger "Manual Deploy"

### 7.2 Rate Limit en Login

- Esperar 5 minutos
- O trigger redeploy para resetear

### 7.3 Error "Module Not Found" en QA

1. Ver logs en Render
2. Comunes: dependencias faltantes
3. Trigger rebuild

### 7.4 Base de Datos Corrupta en QA

- Render free tier no permite acceso directo
- Opcion: esperar a que se auto-reinicie
- O: buscar en logs si hay corruption

---

## 8. FLUJO DE TRABAJO

```
1. DESARROLLO (Local)
   - Codigo en F:\
   - Probar en localhost:8000
   - Backup antes de cambios

2. SUBIR CAMBIOS
   - git add .
   - git commit -m "mensaje"
   - git push origin main

3. QA (Auto-Deploy)
   - Espera 2-5 min
   - Prueba en iso27001-qa.onrender.com
   - Si hay bugs → volver a paso 1

4. PRODUCCION
   - git checkout production
   - git merge main
   - git push origin production
   - Espera 2-5 min
   - Prueba en iso27001-prod.onrender.com
```

---

*Manual creado para acceso independiente a las plataformas.*
