# CHANGELOG - Registro de Cambios

Todos los cambios significativos del proyecto se documentan aqui.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

---

## [v1.1.0] - 2026-03-22

### Agregado
- **UI moderna completa** - Rediseño total de la interfaz con sidebar oscuro, reloj en tiempo real, iconos Font Awesome 6, tema de colores profesional (indigo/blue)
- **Pagina de login profesional** - Tarjeta flotante con animacion, iconos en campos, efecto de brillo en boton, fondo gradiente con orbos animados
- **Audit Log** - Log de todas las acciones del sistema (login, logout, creacion de usuarios, creacion de evaluaciones, cambio de estado)
- **93 controles ISO 27001:2022** - Actualizacion de la base de datos con los 93 controles oficiales reorganizados en 4 dominios (Organizacionales 37, Personas 8, Fisicos 14, Tecnologicos 34)
- **Estadisticas con graficos** - Chart.js con grafico de barras horizontal y grafico radar para perfil de madurez
- **Montaje de archivos estaticos** - `/static` y `/uploads` montados correctamente en FastAPI
- **Validacion en creacion de usuarios** - Verificacion de que el cliente existe antes de crear usuario
- **Dashboard con reloj en tiempo real** - Reloj que se actualiza cada segundo usando JavaScript
- **KPI cards con iconos** - Tarjetas de metricas con iconos, colores y gradientes

### Corregido
- `base.html` - Error de bloque duplicado que causaba 500 en todas las paginas
- `rfcs.py` - Faltaba importar `desc` de sqlalchemy
- `dashboard.py` - Faltaba importar `desc` y `SESSION_COOKIE_NAME`
- `stats.py` - Faltaba importar `RedirectResponse`
- `auth.py` - Faltaba audit log en login/logout exitoso y fallido
- `evaluations.py` - Audit log en crear, iniciar, completar y eliminar evaluacion
- `users.py` - Audit log en crear usuario, validacion de cliente existente

### Cambiado
- `base.html` - Sidebar colapsable con `app-layout sidebar-collapsed`
- `login.html` - Estilos inline profesionales con animaciones
- `dashboard/index.html` - KPIs con iconos, score con color condicional
- `evaluations/list.html` - Tabla con barra de progreso
- `rfcs/list.html` - Badges de prioridad y riesgo con gradientes
- `documents/list.html` - Version tags con estilo
- `sprints/list.html` - Metricas de items completados
- `stats/report.html` - Graficos con etiquetas cortas y guarded checks
- `style.css` - Paleta de colores profesional, sidebar, topbar, tarjetas, badges, tablas, formularios

---

## [v1.0.0] - 2026-03-22

### Agregado
- **Arquitectura FastAPI + SQLModel + SQLite**
- **Sistema de autenticacion** - 4 roles (superadmin, admin_cliente, evaluador, vista_solo)
- **93 controles ISO 27001** - Datos iniciales seedeados en la base de datos
- **Modulo de Evaluaciones** - CRUD completo con madurez CMMI (0-5) y evidencia
- **Modulo de Documentos** - Versionado semver, diff, rollback, workflow de aprobacion
- **Modulo de RFCs** - Solicitudes de cambio ITIL con 4 niveles de riesgo y calculo automatico de prioridad
- **Modulo de Sprints** - Backlog + sprints + tareas vinculadas a controles ISO
- **Dashboard con estadisticas** - KPIs, score de madurez, evaluaciones recientes
- **Import/Export Excel** - Integracion con pandas + openpyxl
- **Scripts de gestion** - backup.py (backup/restore/list), rollback.py (Git-based)
- **Docker y docker-compose** - Despliegue en contenedor
- **Documentacion inicial** - README.md, AGENTS.md
