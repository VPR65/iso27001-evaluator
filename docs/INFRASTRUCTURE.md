# INFRAESTRUCTURA Y PLATAFORMAS - ISO 27001 Evaluator

> Version: 1.1.2 | Ultima actualizacion: 2026-03-23

---

## 1. ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DESARROLLO (Tu PC Local)                             │
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐    │
│   │  VS Code     │────►│  GitHub      │     │  Python/FastAPI     │    │
│   │  (Editor)    │     │  (Codigo)    │     │  (app main:app)     │    │
│   └──────────────┘     └──────┬───────┘     └──────────┬───────────┘    │
│                                │                           │                 │
│                                │ push/pull               │ uvicorn          │
│                                ▼                           ▼                 │
│                         ┌──────────────┐     ┌──────────────────────┐    │
│                         │  GitHub      │     │  PostgreSQL (Neon)           │    │
│                         │  Repository   │     │  (database.db)       │    │
│                         └──────┬───────┘     └──────────────────────┘    │
│                                │                                            │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │ pull
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        QA / STAGING (Render Free)                            │
│   URL: https://iso27001-evaluator.onrender.com                            │
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐    │
│   │  Auto-deploy │────►│  Build       │────►│  Python/FastAPI      │    │
│   │  desde GitHub │     │  Docker      │     │  (app main:app)     │    │
│   └──────────────┘     └──────────────┘     └──────────┬───────────┘    │
│                                                          │                 │
│                                                          │                 │
│                                                          ▼                 │
│                                                 ┌──────────────────┐        │
│                                                 │  PostgreSQL (Neon)        │        │
│                                                 │  (production.db)  │        │
│                                                 └──────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
                                 │ Evaluaciones reales
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PRODUCCION (Render Free o VPS)                       │
│   URL: Tu dominio personalizado o tunombre.onrender.com                    │
│                                                                              │
│   ┌──────────────┐     �──────────────┐     ┌──────────────────────┐    │
│   │  Usuarios    │────►│  FastAPI      │────►│  PostgreSQL (Neon)           │    │
│   │  Reales      │     │  + Uvicorn    │     │  (database.db)       │    │
│   └──────────────┘     └───────────────┘     └──────────────────────┘    │
│                                                                              │
│                         Backup automatico: Render hace snapshot diario       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PLATAFORMAS POR ENTORNO

### 2.1 Resumen Comparativo

| Plataforma         | Uso                  | Costo | Python | PostgreSQL | SSL | Dominio       |
|-------------------|----------------------|-------|--------|--------|-----|---------------|
| Tu PC local        | Desarrollo           | $0    | Si     | Si     | No  | localhost     |
| GitHub             | Control de versiones | $0    | -      | -      | -   | github.com    |
| Render             | QA + Produccion     | $0    | Si     | Si     | Si  | .onrender.com|
| Cloudflare         | Tunneling (alternativa)| $0  | -      | -      | Si  | Tunel        |
| PythonAnywhere     | Produccion (alternativa)| $0 | Si     | Limitado| Si | .pythonanywhere.com |

### 2.2 Detalle por Plataforma

---

### PLATAFORMA 1: TU PC LOCAL (Desarrollo)

```
╔════════════════════════════════════════════════════════════╗
║              ENTORNO: DESARROLLO LOCAL                    ║
╚════════════════════════════════════════════════════════════╝

  Herramientas instaladas:
  ┌─────────────────┬──────────────────────────────────┐
  │ Python 3.12+   │ Runtime de la aplicacion        │
  │ VS Code         │ Editor de codigo (gratis)       │
  │ Git             │ Control de versiones (gratis)    │
  │ GitHub Desktop  │ GUI para Git (gratis)         │
  │ Chrome/Firefox  │ Navegador para pruebas          │
  └─────────────────┴──────────────────────────────────┘

  Flujo de trabajo:
  1. Editas codigo en VS Code
  2. Ejecutas: uvicorn app.main:app --reload
  3. Pruebas en: http://localhost:8000
  4. Commits en Git local
  5. Push a GitHub
```

| Recurso | Valor |
|---------|-------|
| Costo mensual | $0 |
| Almacenamiento | Tu disco duro |
| Memoria RAM | Tu PC (minimo 4GB) |
| CPU | Tu procesador |
| Acceso internet | Tu conexion |
| IP publica | No (solo localhost) |

---

### PLATAFORMA 2: GITHUB (Control de Versiones)

```
╔════════════════════════════════════════════════════════════╗
║              CONTROL DE VERSIONES - GITHUB               ║
╚════════════════════════════════════════════════════════════╝

  Repository: iso27001-evaluator

  Ramas:
  ┌──────────────────────────────────────────────────────────┐
  │  production ── etiquetas de release ──► Render Prod    │
  │    │                                                     │
  │    └── merge desde main (despues de QA OK)             │
  │                                                         │
  │  main ────────────────► Render QA                      │
  │    │                                                     │
  │    └── feature/nombre (desarrollo)                       │
  └──────────────────────────────────────────────────────────┘

  Tags de version:
  v1.0.0 ────── v1.1.0 ────── v1.1.2 ────── v1.2.0 (futuro)

  Integracion: Push automatico triggerea deploy en Render (QA o Prod segun rama)
```

| Recurso | Valor |
|---------|-------|
| Cuenta | github.com (gratis) |
| Repositorios publicos | Ilimitados |
| Repositorios privados | Ilimitados (en plan free) |
| Actions CI/CD | 2,000 min/mes gratis |
| Almacenamiento | 500MB por repo |
| Ancho de banda | 100GB/mes |

---

### PLATAFORMA 3: RENDER (QA + Produccion)

```
╔════════════════════════════════════════════════════════════╗
║              HOSTING - RENDER.COM (GRATIS)             ║
╚════════════════════════════════════════════════════════════╝

  Plan libre: 750 horas/mes
  (Si usas 1 servicio, dura ~31 dias con 24h activo)

   ┌─────────────────────────────────────────────────────────┐
   │                                                         │
   │   GitHub Repo                                          │
   │        │                                                │
   │        ▼ (push a main)                                 │
   │   QA: iso27001-qa.onrender.com (rama main)            │
   │        │                                                │
   │        ▼ (merge a production)                          │
   │   Prod: iso27001-prod.onrender.com (rama production)   │
   │                                                         │
   │   Build: pip install -r requirements.txt                │
   │   Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT │
   │   SSL: ✓ Automatico                                     │
   │                                                         │
   └─────────────────────────────────────────────────────────┘

   Render QA - iso27001-qa:
   ┌─────────────────────────┬──────────────────────────────┐
   │ Name                   │ iso27001-qa                  │
   │ Region                 │ Oregon                       │
   │ Branch                 │ main                         │
   │ Root Directory         │ (vacio)                      │
   │ Environment            │ Python 3                     │
   │ Build Command          │ pip install -r requirements.txt│
   │ Start Command          │ uvicorn app.main:app         │
   │                        │ --host 0.0.0.0               │
   │                        │ --port $PORT                 │
   │ Plan                   │ Free                         │
   └─────────────────────────┴──────────────────────────────┘

   Render Prod - iso27001-prod:
   ┌─────────────────────────┬──────────────────────────────┐
   │ Name                   │ iso27001-prod                │
   │ Region                 │ Oregon                       │
   │ Branch                 │ production                   │
   │ Root Directory         │ (vacio)                      │
   │ Environment            │ Python 3                     │
   │ Build Command          │ pip install -r requirements.txt│
   │ Start Command          │ uvicorn app.main:app         │
   │                        │ --host 0.0.0.0               │
   │                        │ --port $PORT                 │
   │ Plan                   │ Free                         │
   └─────────────────────────┴──────────────────────────────┘
```

| Recurso | Valor |
|---------|-------|
| Web Services | 1 gratis |
| Horas mensuales | 750 horas |
| CPU compartido | 0.5 CPU |
| RAM | 512MB |
| Disco | 1GB |
| Ancho de banda | 100GB/mes |
| SSL | Gratis y automatico |
| Dominio | .onrender.com gratis |
| Dominio personalizado | $0 (con verificacion) |
| Base de datos | PostgreSQL $0/mes (limitado) |
| Deploy automatico | Si (desde GitHub) |

**Nota sobre el plan gratuito:** La app "duerme" despues de 15 minutos de inactividad. Despierta automaticamente cuando alguien la accede. Esto es aceptable para una herramienta interna de evaluacion ISO 27001.

---

### PLATAFORMA 4: CLOUDFLARE TUNNEL (Alternativa - 100% Local + Online)

```
╔════════════════════════════════════════════════════════════╗
║           TUNNEL CLOUDFLARE - TU PC COMO SERVIDOR       ║
╚════════════════════════════════════════════════════════════╝

  Si NO quieres usar Render y prefieres alojar desde tu PC:

  Tu PC (localhost:8000)
        │
        │ cloudflared tunnel
        ▼
  ┌──────────────────┐
  │  Cloudflare      │
  │  Tunnel (gratis) │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │  URL publica:    │
  │  tunombre.trycloudflare.com │
  └──────────────────┘

  Ventajas: 100% gratuito, sin limite de horas
  Desventajas: Tu PC debe estar prendido
```

| Recurso | Valor |
|---------|-------|
| Cloudflare Tunnel | $0 |
| Dominio | .trycloudflare.com |
| SSL | Gratis |
| Ancho de banda | Ilimitado |
| Horas limite | Ninguna |

---

## 3. FLUJO DE DESARROLLO COMPLETO

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    FLUJO DE DESARROLLO COMPLETO                       ║
╚═══════════════════════════════════════════════════════════════════════╝

 DESARROLLO                    QA/STAGING                   PRODUCCION
 (Tu PC)                      (Render main)                (Render prod)
 ──────────                    ──────────────                ──────────────

 1. Crear rama feature         6. Push a main              10. Merge a prod
    git checkout -b             git push origin              git checkout prod
    feature/mi-cambio          main                         git merge main
    │                          │                            git push prod
    ▼                          ▼                            │
 2. Programar cambio       7. QA auto-deploy              ▼
    en VS Code          https://iso27001-           11. Prod auto-deploy
    │                    qa.onrender.com            https://iso27001-prod
    ▼                          │                            │
 3. Probar local          8. Probar todo OK              12. Verificar prod
    uvicorn                 en QA                         │
    app.main:app --reload   │                             ▼
    │                        ▼                       13. Tag version
 4. Commit                 9. Si hay bugs:           git tag v1.2.0
    git add .               volver a paso 1              -m "Release..."
    git commit -m            con fix en main              │
    "feat: cambio"           en nueva rama                 ▼
    │                        │                       14. Usuarios finales
 5. Push                   Si todo OK ->                  usan prod
    git push origin          ir a paso 10                 │
    feature/mi-cambio        para promotion                ▼
                                                     15. Feedback
                                                     del usuario -> RFC

```

---

## 4. PASOS PARA CONFIGURAR TODO (Gratis)

### Paso 1: Tu PC Local (Ya tienes)

```bash
# Ya tienes todo instalado
python --version     # Python 3.12+
git --version       # Git
code --version      # VS Code
```

### Paso 2: Subir codigo a GitHub

```bash
# 1. Crear repo en github.com (gratis, cuenta nueva)

# 2. En tu PC, dentro del proyecto:
cd "C:/Users/vpalma/Documents/Desarrollo/OpenCode_Antigravity/ISO27001_ITIL_seguridad"
git init
git add .
git commit -m "feat: proyecto inicial ISO 27001 Evaluator v1.1.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/iso27001-evaluator.git
git push -u origin main
```

### Paso 3: Configurar Render (Gratis)

```
1. Ir a: https://render.com
2. Crear cuenta gratuita (GitHub login)
3. New + Web Service
4. Conectar tu GitHub repo
5. Configurar:
   - Name: iso27001-evaluator
   - Branch: main
   - Region: Oregon
   - Root Directory: (vacio)
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   - Plan: Free
6. Create Web Service
7. Esperar build (~2-3 minutos)
8. Listo! URL: https://iso27001-evaluator.onrender.com
```

### Paso 4: Desplegar actualizaciones automaticamente

Cada vez que hagas `git push origin main`, Render detecta el cambio y hace deploy automatico.

---

## 5. BACKUP Y RECUPERACION EN RENDER

```
╔════════════════════════════════════════════════════════════╗
║              BACKUP Y RECUPERACION                         ║
╚════════════════════════════════════════════════════════════╝

  Render hace:
  ┌─────────────────────────────────────────────┐
  │  snapshots automaticos (hasta 3 dias)       │
  │  Rollback a deploy anterior (1 click)       │
  └─────────────────────────────────────────────┘

  Para restaurar:
  1. Render Dashboard
  2. Tu Web Service
  3. History
  4. Seleccionar version anterior
  5. Rollback

  Backup local adicional (tu PC):
  ┌─────────────────────────────────────────────┐
  │  python scripts/backup.py backup            │
  │  (guarda en backups/backup_YYYYMMDD.zip)     │
  └─────────────────────────────────────────────┘
```

---

## 6. COSTO TOTAL MENSUAL

```
╔════════════════════════════════════════════════════════════╗
║              COSTO TOTAL MENSUAL: $0                      ║
╚════════════════════════════════════════════════════════════╝

  ┌──────────────────────┬──────────┬─────────────────────┐
  │ Servicio              │ Costo    │ Notas                │
  ├──────────────────────┼──────────┼─────────────────────┤
  │ Tu PC local          │ $0       │ Ya tienes PC         │
  │ GitHub               │ $0       │ Plan gratis         │
  │ Render (1 servicio)  │ $0       │ 750h/mes gratis     │
  │ Dominio .onrender.com │ $0       │ Incluido            │
  │ SSL                  │ $0       │ Automatico          │
  │ Cloudflare (opcional)│ $0       │ Si usas tunnel      │
  ├──────────────────────┼──────────┼─────────────────────┤
  │ TOTAL MENSUAL        │ $0       │                     │
  └──────────────────────┴──────────┴─────────────────────┘
```

---

## 7. LIMITACIONES CONOCIDAS

| Limitacion               | Solucion                               |
|-------------------------|----------------------------------------|
| Render free: duerme 15min | Aceptable para uso interno ISO 27001  |
| 750 horas/mes          | Suficiente para 1 app de evaluacion   |
| PostgreSQL Neon 0.5GB    | Suficiente para miles de evaluaciones |
| Sin dominio propio      | Usar .onrender.com (o comprar uno)  |
| Sin email integrado     | Usar email externo (Gmail, etc.)     |
| Sin cron jobs automaticos| Ejecutar manualmente o usar Render Cron |

---

## 8. PROXIMOS PASOS PARA CONFIGURAR

```bash
# 1. Crear cuenta GitHub (si no tienes)
# https://github.com/signup

# 2. Crear repositorio nuevo en GitHub

# 3. Subir codigo local a GitHub
git init
git add .
git commit -m "feat: ISO 27001 Evaluator v1.1.0"
git remote add origin https://github.com/TU_USUARIO/iso27001-evaluator.git
git push -u origin main

# 4. Crear cuenta Render (gratis)
# https://render.com/register

# 5. Conectar GitHub y desplegar

# 6. Probar la URL de produccion
```
