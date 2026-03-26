# 🏗️ Diagrama Maestro del Ecosistema ISO 27001 Evaluator

Este documento describe **completamente** la arquitectura, herramientas, entornos y flujos de datos del sistema desarrollado.

---

## 1. Visión General de Entornos

El sistema opera en tres entornos claramente diferenciados, conectados mediante **Git** y **Neon.tech** (Base de datos).

```text
┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
│   DESARROLLO (Local) │       │        QA            │       │   PRODUCCIÓN (Prod)  │
│   Tu PC (Windows)    │       │  Render.com (Free)   │       │  Render.com (Prod)   │
│                      │       │                      │       │                      │
│  - Código Fuente     │──────▶│  - Versión Estable   │──────▶│  - Versión Final     │
│  - Pruebas Unitarias │  Git  │  - Datos Prueba      │  Git  │  - Datos Reales      │
│  - Debugging         │ Push  │  - Validación IA     │ Push  │  - IA Activa         │
│  - SQLModel (PostgreSQL) │       │  - Neon.tech (QA)    │       │  - Neon.tech (Prod)  │
└──────────────────────┘       └──────────────────────┘       └──────────────────────┘
         │                            │                              │
         │                            │                              │
         └────────────────────────────┼──────────────────────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │   BASE DE DATOS (DB)    │
                         │   Neon.tech (PostgreSQL)│
                         │                         │
                         │  - Persistencia Central │
                         │  - Multi-tenant         │
                         │  - Backups automáticos  │
                         └─────────────────────────┘
```

---

## 2. Arquitectura Técnica Detallada

### 2.1. Stack Tecnológico (Herramientas)

| Capa | Tecnología | Función |
| :--- | :--- | :--- |
| **Frontend** | HTML5 + Jinja2 + HTMX | Interfaz de usuario dinámica sin JavaScript complejo. |
| **Estilos** | Pico.css + CSS Personalizado | Diseño limpio, responsivo y moderno. |
| **Backend** | Python 3.12 + FastAPI | Lógica de negocio, rápida y asíncrona. |
| **ORM** | SQLModel | Interacción con la base de datos (SQLAlchemy + Pydantic). |
| **Base de Datos** | PostgreSQL (Neon.tech) | Almacenamiento persistente de datos. |
| **IA / ML** | NVIDIA NIM (Llama 3.1 70B) | Análisis de controles y recomendaciones. |
| **Tests** | Pytest + TestClient | Pruebas automatizadas de regresión. |
| **Despliegue** | Render.com | Hosting de la aplicación (QA y Prod). |
| **Control** | Git + GitHub | Versionado y CI/CD básico. |

### 2.2. Diagrama de Flujo de Datos (Data Flow)

Así viaja la información desde que el usuario hace clic hasta que ve el resultado:

```text
USUARIO (Navegador)
      │
      ▼
[ Frontend: Pico.css + HTMX ] ◀─── Renderiza plantillas Jinja2
      │
      ▼ (HTTP Request)
[ Backend: FastAPI (app/main.py) ]
      │
      ├───▶ [ Auth: bcrypt + Cookies ] ────┐ (Verifica sesión)
      │                                    │
      ├───▶ [ Lógica: app/routes/*.py ] ◀──┘ (Procesa acción)
      │         │
      │         ├───▶ [ DB: Neon PostgreSQL ] ◀── (Lee/Escribe datos)
      │         │
      │         └───▶ [ IA Service: app/ai_service.py ]
      │                   │
      │                   ▼
      │             [ NVIDIA NIM Cloud ]
      │             (Llama 3.1 70B)
      │                   │
      │                   ▼
      │             (Respuesta JSON)
      │
      ▼ (HTML Response)
[ Navegador del Usuario ]
```

---

## 3. Detalle de Componentes Críticos

### 3.1. Base de Datos (Neon.tech PostgreSQL)
*   **Función:** Corazón del sistema. Guarda usuarios, clientes, evaluaciones, respuestas y auditorías.
*   **Características:**
    *   **Multi-tenant:** Separación estricta de datos por `client_id`.
    *   **Persistencia:** Datos seguros en la nube (AWS).
    *   **Escalabilidad:** Plan gratuito generoso (0.5 GB).
*   **Tablas Principales:** `User`, `Client`, `Evaluation`, `ControlResponse`, `Norma`, `ControlDefinition`, `AuditLog`.

### 3.2. Inteligencia Artificial (NVIDIA NIM)
*   **Motor:** `meta/llama-3.1-70b-instruct`.
*   **Ubicación:** Nube de NVIDIA (no consume recursos locales).
*   **Casos de Uso:**
    1.  **Análisis de Respuestas:** Evalúa si la evidencia es suficiente.
    2.  **Recomendaciones:** Sugiere acciones para controles no conformes.
    3.  **Resumen Ejecutivo:** Redacta informes para gerencia.
*   **Seguridad:** La API Key se gestiona mediante variables de entorno (`NVIDIA_API_KEY`).

### 3.3. Pruebas de Calidad (QA Testing)
*   **Herramienta:** `pytest`.
*   **Cobertura:**
    *   **Modelos:** Verifica que las tablas existan.
    *   **Auth:** Prueba logins y denegaciones.
    *   **Flujos:** Simula creaciones de evaluaciones completas.
    *   **Admin:** Valida altas/bajas de usuarios y clientes.
*   **Ejecución:** `python -m pytest tests/ -v` (Se ejecuta antes de cada deploy).

### 3.4. Seguridad (Security)
*   **Contraseñas:** Hasheadas con `bcrypt` (imposibles de leer en texto plano).
*   **Sesiones:** Cookies seguras (`httponly`, `samesite`).
*   **CSRF:** Tokens de protección en todos los formularios.
*   **Roles:** Superadmin, Admin Cliente, Evaluador, Solo Vista.

---

## 4. Ciclo de Vida del Desarrollo (SDLC)

El proceso para llevar un cambio desde la idea hasta el usuario final:

1.  **Desarrollo (Local):**
    *   Se crea una rama `feature/nombre`.
    *   Se escribe código y pruebas (`tests/`).
    *   Se ejecuta `pytest` localmente.
2.  **Integración (QA):**
    *   Se hace merge a `main`.
    *   GitHub Actions (o deploy manual) actualiza **Render QA**.
    *   Se limpian datos de prueba (`/admin/debug/reset-all`).
    *   Se valida funcionalidad con datos reales de QA.
3.  **Producción (Prod):**
    *   Se etiqueta la versión (`git tag v1.4.1`).
    *   Se despliega a **Render Prod**.
    *   Se valida el "health check" (`/health`).

---

## 5. Estructura de Archivos Clave

```text
app/
├── main.py                 # Punto de entrada (FastAPI)
├── ai_service.py           # 🤖 Lógica de conexión con NVIDIA IA
├── database.py             # Conexión a Neon PostgreSQL
├── models.py               # Definición de tablas (SQLModel)
├── seed.py                 # Datos iniciales (Normas ISO, ITIL4)
├── auth.py                 # Seguridad y usuarios
├── routes/
│   ├── admin.py            # Panel de administración
│   ├── evaluations.py      # Lógica de evaluaciones
│   ├── ai_routes.py        # Endpoints para la IA
│   └── ...
└── templates/              # Vistas HTML (Jinja2)

tests/
├── conftest.py             # Configuración de pruebas
├── test_admin_panel.py     # Tests del panel admin
├── test_models.py          # Tests de modelos
└── ...

docs/
├── ARCHITECTURE.md         # Detalle técnico
├── EXPLICACION_IA.md       # Diagrama IA para no técnicos
├── MASTER_DIAGRAM.md       # ESTE ARCHIVO
└── CHANGELOG.md            # Historial de cambios
```

---

## 6. Resumen de Versiones

| Componente | Versión / Detalle |
| :--- | :--- |
| **Proyecto** | **v1.4.1** |
| **Python** | 3.12+ |
| **Framework** | FastAPI 0.110+ |
| **DB** | PostgreSQL 15 (Neon) |
| **IA Model** | Llama 3.1 70B Instruct |
| **Normas** | ISO 27001:2022 (93 controles), ITIL v4 (34 prácticas), ISO 9001, 20000, 22301 |

---

> **Nota:** Este documento sirve como referencia maestra para entender cómo interactúan todas las piezas del rompecabezas. Cualquier cambio en la arquitectura debe reflejarse aquí.
