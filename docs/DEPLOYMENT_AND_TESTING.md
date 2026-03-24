# GUIA DE DESPLIEGUE Y PRUEBAS FUNCIONALES

> Version: 1.0.0 | Fecha: 2026-03-24

---

## 1. ARQUITECTURA DE ENTORNOS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ISO 27001 EVALUATOR                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐ │
│  │   DESARROLLO    │      │       QA         │      │   PRODUCCION     │ │
│  │   (localhost)   │ ───► │   (Render.com)   │ ───► │   (Render.com)   │ │
│  │                 │ push │                  │ push │                  │ │
│  │  Puerto: 8000   │      │  iso27001-qa     │      │ iso27001-prod    │ │
│  │  SQLite local   │      │  Branch: main    │      │ Branch: prod     │ │
│  └──────────────────┘      └──────────────────┘      └──────────────────┘ │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                         GITHUB REPOSITORY                          │   │
│  │               https://github.com/VPR65/iso27001-evaluator          │   │
│  │                                                                     │   │
│  │   main (QA)  ◄──────────────────────────────────────────────┐      │   │
│  │                                                        │      │      │
│  │   production  ◄───────────────────────────────────────────┘      │   │
│  │                                                                     │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CREDENCIALES Y DATOS DE ACCESO

### 2.1 Credenciales de Aplicacion

| Entorno | URL | Usuario | Password | Rol |
|---------|-----|---------|----------|-----|
| Desarrollo | http://localhost:8000 | admin@iso27001.local | admin123 | SUPERADMIN |
| Desarrollo | http://localhost:8000 | admin@demo.local | demo123 | ADMIN_CLIENTE |
| QA | https://iso27001-qa.onrender.com | admin@iso27001.local | admin123 | SUPERADMIN |
| Produccion | https://iso27001-prod.onrender.com | admin@iso27001.local | admin123 | SUPERADMIN |

### 2.2 Cuentas de Servicios

| Servicio | Cuenta | Notas |
|----------|--------|-------|
| GitHub | vpalma05@hotmail.com | Usuario: VPR65 |
| Render | vpalma05@hotmail.com | Login via GitHub |

---

## 3. LEVANTAR SERVICIOS

### 3.1 Desarrollo Local (TU PC)

**Paso 1: Abrir terminal**

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
```

**Paso 2: Verificar que la DB existe**

```cmd
dir iso27001.db
```

Si no existe, crearla:

```cmd
python -c "from app.main import app; print('OK')"
```

**Paso 3: Iniciar servidor**

```cmd
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Paso 4: Verificar que levanto**

Navegador: http://localhost:8000

Deberia mostrar la pagina de login.

---

### 3.2 QA (Render.com)

QA se despliega automaticamente cuando se hace push a la rama `main`.

**Para actualizar QA:**

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
git add .
git commit -m "tu mensaje"
git push origin main
```

**Verificar que el deploy termino:**

1. Ir a: https://dashboard.render.com
2. Seleccionar servicio: `iso27001-qa`
3. Ver en "Events" que dice "Deploy completed"
4. Probar: https://iso27001-qa.onrender.com

**Tiempo estimado:** 2-5 minutos

---

### 3.3 Produccion (Render.com)

Produccion se despliega automaticamente cuando se hace push a la rama `production`.

**Para actualizar Produccion:**

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
git checkout production
git merge main
git push origin production
```

**Verificar que el deploy termino:**

1. Ir a: https://dashboard.render.com
2. Seleccionar servicio: `iso27001-prod`
3. Ver en "Events" que dice "Deploy completed"
4. Probar: https://iso27001-prod.onrender.com

**Tiempo estimado:** 2-5 minutos

---

## 4. FLUJO DE TRABAJO RECOMENDADO

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE DESPLIEGUE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   1. DESARROLLO (local)                                                │
│      ┌─────────────────────────────────────────┐                       │
│      │ a) Hacer cambios en codigo               │                       │
│      │ b) Probar en localhost:8000             │                       │
│      │ c) Verificar con: python -c "from       │                       │
│      │       app.main import app; print('OK')"  │                       │
│      │ d) git add . && git commit -m "..."     │                       │
│      └──────────────────┬──────────────────────┘                       │
│                         │                                               │
│                         ▼                                               │
│   2. QA (Render)        │                                               │
│      ┌─────────────────────────────────────────┐                       │
│      │ a) git push origin main                │                       │
│      │ b) Esperar 2-5 min (auto-deploy)         │                       │
│      │ c) Probar en iso27001-qa.onrender.com  │                       │
│      │ d) Si hay bugs → volver a paso 1        │                       │
│      └──────────────────┬──────────────────────┘                       │
│                         │                                               │
│                         ▼                                               │
│   3. PRODUCCION        │                                               │
│      ┌─────────────────────────────────────────┐                       │
│      │ a) git checkout production              │                       │
│      │ b) git merge main                       │                       │
│      │ c) git push origin production           │                       │
│      │ d) Esperar 2-5 min (auto-deploy)        │                       │
│      │ e) Probar en iso27001-prod.onrender.com│                       │
│      └─────────────────────────────────────────┘                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. PRUEBAS FUNCIONALES

### 5.1 Checklist de Pruebas Basicas

**Antes de pasar a Produccion, verificar:**

| # | Prueba | URL | Esperado | OK |
|---|--------|-----|----------|---|
| 1 | Login superadmin | /login | Pagina de login carga | [ ] |
| 2 | Login valido | /login → admin@iso27001.local / admin123 | Redirige a /dashboard | [ ] |
| 3 | Login invalido | /login → credenciales incorrectas | Muestra error | [ ] |
| 4 | Logout | Click en logout | Redirige a /login | [ ] |
| 5 | Dashboard | /dashboard | Muestra KPIs, graficos | [ ] |
| 6 | Listar evaluaciones | /evaluations | Muestra lista de evaluaciones | [ ] |
| 7 | Ver evaluacion | /evaluations/{id} | Muestra detalle con controles | [ ] |
| 8 | Evaluar control | /evaluate/{eval_id}/control/{ctrl_id} | Formulario de evaluacion | [ ] |
| 9 | Guardar evaluacion | Submit en evaluar control | Guarda y muestra exito | [ ] |
| 10 | Crear usuario admin | /admin/all-users | Formulario con cliente y rol | [ ] |

### 5.2 Checklist de Pruebas de Modulos

| Modulo | Prueba | URL | Esperado |
|--------|--------|-----|----------|
| **Clientes** | Listar clientes | /clients | Muestra clientes |
| **Clientes** | Crear cliente | /clients/new → form | Cliente creado |
| **Evaluaciones** | Nueva evaluacion | /evaluations/new → form | Evaluacion creada con 93 controles |
| **Evaluaciones** | Iniciar evaluacion | /evaluations/{id}/start | Estado cambia a in_progress |
| **Evaluaciones** | Completar evaluacion | /evaluations/{id}/complete | Estado cambia a completed |
| **Evaluar** | Guardar madurez | Control → maturity 1-5 | Guarda correctamente |
| **Evaluar** | Subir evidencia | Subir archivo | Archivo guardado |
| **Estadisticas** | Ver graficos | /stats/{id} | Bar chart + radar chart |
| **Documentos** | Crear documento | /documents/new | Documento creado |
| **Documentos** | Nueva version | /documents/{id} → agregar version | Version creada |
| **RFCs** | Crear RFC | /rfcs/new | RFC creado |
| **RFCs** | Cambiar estado | /rfcs/{id}/status | Estado cambia |
| **Sprints** | Crear sprint | /sprints/new | Sprint creado |
| **Sprints** | Agregar item | /sprints/{id}/add-item | Item en backlog |
| **Import/Export** | Exportar Excel | /import-export/export/{id} | Descarga archivo .xlsx |
| **Import/Export** | Importar Excel | /import-export/import → subir archivo | Datos importados |

---

## 6. COMANDOS DE VERIFICACION

### 6.1 Verificar que el codigo compila

```cmd
cd "F:\Desarrollo\Opencode\ISO27001_ITIL_seguridad"
python -c "from app.main import app; print('OK')"
```

**Resultado esperado:** `OK`

### 6.2 Verificar rutas registradas

```cmd
python -c "
from app.main import app
for route in app.routes:
    if hasattr(route, 'path'):
        print(route.path)
"
```

### 6.3 Verificar base de datos

```cmd
# Contar evaluaciones
python -c "
from app.database import engine
from sqlmodel import Session, select, func
from app.models import Evaluation
with Session(engine) as s:
    print('Evaluaciones:', s.exec(select(func.count(Evaluation.id))).first())
"
```

### 6.4 Verificar usuarios

```cmd
python -c "
from app.database import engine
from sqlmodel import Session, select
from app.models import User
with Session(engine) as s:
    for u in s.exec(select(User)).all():
        print(f'{u.email} - {u.role.value}')
"
```

---

## 7. RESOLUCION DE PROBLEMAS

### 7.1 Error "ModuleNotFoundError"

**Problema:** Faltan dependencias

**Solucion:**
```cmd
pip install -r requirements.txt
```

### 7.2 Error "Database is locked"

**Problema:** Otra conexion esta usando la DB

**Solucion:** Cerrar otras instancias del server

### 7.3 Pagina en blanco en Render

**Problema:** La app noLevanto

**Solucion:**
1. Ir a https://dashboard.render.com
2. Seleccionar el servicio
3. Ver "Logs" para ver el error
4. Comunmente: faltante de dependencia o error de sintaxis

### 7.4 Cambios no se ven en QA/Prod

**Problema:** No se hizo push

**Solucion:**
```cmd
git push origin main          # para QA
git push origin production    # para Prod
```

### 7.5 "CSRF token invalid" en todos los forms

**Problema:** Token expirado o no se esta pasando

**Solucion:** Refrescar la pagina (F5)

---

## 8. RESUMEN DE URLs

| Entorno | URL | Proposito |
|---------|-----|-----------|
| Desarrollo | http://localhost:8000 | Pruebas locales |
| Login | http://localhost:8000/login | Autenticacion |
| Dashboard | http://localhost:8000/dashboard | KPIs |
| Evaluaciones | http://localhost:8000/evaluations | Lista |
| Admin Users | http://localhost:8000/admin/all-users | Gestion usuarios |
| | | |
| QA | https://iso27001-qa.onrender.com | Pre-produccion |
| QA Login | https://iso27001-qa.onrender.com/login | |
| QA Dashboard | https://iso27001-qa.onrender.com/dashboard | |
| | | |
| Prod | https://iso27001-prod.onrender.com | Produccion |
| Prod Login | https://iso27001-prod.onrender.com/login | |
| Prod Dashboard | https://iso27001-prod.onrender.com/dashboard | |

---

## 9. VERSION ACTUAL

**Version del codigo:** v1.1.2

**Ultimos cambios:**
- AuditLog en todos los POST handlers
- Fix admin user creation (requiere cliente y rol)
- Fix evaluation detail view
- Fix document publish endpoint

---

*Documento creado para pruebas funcionales y despliegue. Actualizar con cada cambio significativo.*
