# 🌐 MODOS DE DESPLIEGUE - ISO 27001 Evaluator

**Versión:** v2.0.0  
**Fecha:** 2026-03-31  
**Estado:** Documentación actualizada

---

## 🎯 Los 3 Modos de Despliegue

El proyecto soporta 3 modos de despliegue según las necesidades del cliente:

| Modo | Nombre | Descripción | Ubicación |
|------|--------|-------------|-----------|
| **A** | **Todo Local** | 100% en tu PC/servidor | On-Premise |
| **B** | **Mixto (Híbrido)** | App en nube, IA+DB local | Oracle VM |
| **C** | **Todo Nube** | 100% en la nube | Render + Neon |

---

## 📊 Comparativa de Modos

| Característica | A: Todo Local | B: Mixto/Híbrido | C: Todo Nube |
|----------------|---------------|------------------|---------------|
| **Aplicación** | Tu PC/Docker | Oracle VM (gratis) | Render.com (gratis) |
| **Base de Datos** | SQLite/PostgreSQL local | Oracle PostgreSQL | Neon.tech (gratis) |
| **IA (Ollama)** | Tu PC | Oracle VM (gratis) | NVIDIA API / Ollama cloud |
| **Almacenamiento** | Tu disco/NAS | Oracle VM | S3/MinIO |
| **Costo** | Hardware ($500+) | $0/mes | $0/mes |
| **Soberanía de datos** | 🔒 Total | 🔒 Alta | ⚠️ Parcial |
| **ISO-Compliant** | ✅ Sí | ✅ Sí | ⚠️ Parcial |
| **Setup** | 30 min | 2 horas | 10 min |
| **Internet requerida** | No | Sí | Sí |

---

## 🌐 Detalle por Modo

### A) MODO: TODO LOCAL (On-Premise)

**Ideal para:** Banca, Gobierno, Empresas con política de datos locales

| Componente | Ubicación |
|------------|-----------|
| App | Tu servidor (Docker) |
| DB | PostgreSQL local |
| IA | Ollama local |
| Storage | NAS/SMB local |

**Requisitos:**
- Servidor con 8GB RAM mínimo
- Docker + Docker Compose
- PostgreSQL 15+
- (Opcional) Ollama para IA local

**Setup:**
```bash
# 1. Clonar repo
git clone https://github.com/VPR65/iso27001-evaluator.git
cd iso27001-evaluator

# 2. Configurar
cp .env.docker .env
# Editar .env con DATABASE_URL=postgresql://...

# 3. Iniciar con Docker
docker-compose up -d
```

**URLs:**
- App: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

---

### B) MODO: MIXTO / HÍBRIDO (Oracle Cloud)

**Ideal para:** Empresas que quieren $0 y control total de datos

| Componente | Ubicación |
|------------|-----------|
| App | Oracle VM (Free Tier) |
| DB | Oracle PostgreSQL (Free Tier) |
| IA | Ollama en la misma VM |
| Storage | Oracle Object Storage |

**Setup (2 horas):**
1. Crear cuenta Oracle Cloud Free Tier
2. Crear VM Ampere A1 (4 OCPUs, 24GB RAM)
3. Instalar Docker + docker-compose
4. Desplegar app
5. Configurar Ollama

**URLs:**
- App: `http://tu-ip-publica:8000` o dominio configurado
- DB: `localhost:5432` (misma VM)

---

### C) MODO: TODO NUBE (Render + Neon)

**Ideal para:** Testing, Demos, startups que buscan velocidad

| Componente | Ubicación |
|------------|-----------|
| App | Render.com (Free Tier) |
| DB | Neon.tech (Free Tier) |
| IA | NVIDIA API / Ollama cloud |
| Storage | Render Disk (1GB efímero) |

**Setup (10 minutos):**
1. Push a GitHub (rama main)
2. Connect a Render.com
3. Configurar DATABASE_URL de Neon
4. Deploy automático

**URLs:**
- QA: `https://iso27001-qa.onrender.com` ✅ Activo
- Prod: `https://iso27001-prod.onrender.com` ⚠️ Inactivo
- Dev: `http://localhost:8000` ✅ Activo

---

## 🔧 Configuración por Modo

### Archivo `.env` según modo:

#### Modo A: Todo Local (SQLite)
```bash
DATABASE_URL=sqlite:///./iso27001.db
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.1:latest
```

#### Modo A: Todo Local (PostgreSQL)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/iso27001
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.1:latest
```

#### Modo B: Híbrido (Oracle)
```bash
DATABASE_URL=postgresql://user:pass@oracle-host/oradb
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.1:latest
```

#### Modo C: Todo Nube (Render + Neon)
```bash
DATABASE_URL=postgresql://user:pass@neon.tech/neondb
AI_MODE=nvidia
NVIDIA_API_KEY=tu_api_key_nvidia
```

---

## 📋 Estados Actuales de los Entornos

| Entorno | URL | Estado | Modo |
|---------|-----|--------|------|
| **Desarrollo** | `http://localhost:8000` | ✅ Activo | A: Todo Local |
| **QA (Render)** | `https://iso27001-qa.onrender.com` | ✅ Activo | C: Todo Nube |
| **Prod (Render)** | `https://iso27001-prod.onrender.com` | ⚠️ Inactivo | C: Todo Nube |

---

## 🚀 ¿Cuál Modo Elegir?

### Elegir A (Todo Local) si:
- ✅ Datos deben stay inside company
- ✅ Compliance ISO 27001 total requerido
- ✅ Presupuesto para hardware
- ✅ IT team disponible para mantenimiento

### Elegir B (Mixto/Híbrido) si:
- ✅ Quieren $0/mes con control total
- ✅ Dispuestos a configurar Oracle Cloud (2h)
- ✅ Datos sensibles pero pueden estar en nube privada
- ✅ Requieren ISO-compliant

### Elegir C (Todo Nube) si:
- ✅ Solo para testing/demo
- ✅ Necesitan fastest setup (<15 min)
- ✅ Aceptan datos en la nube pública
- ✅ Startup con recursos limitados

---

## 📚 Documentación Relacionada

| Documento | Descripción |
|-----------|-------------|
| `docs/DEPLOYMENT_AND_TESTING.md` | Guía de despliegue completa |
| `docs/PLATFORMS_MANUAL.md` | Manual de plataformas (Render, GitHub) |
| `docs/INFRASTRUCTURE.md` | Infraestructura detallada |
| `docs/PROJECT_DEFINITION.md` | Definición completa del proyecto |
| `docker-compose.yml` | Docker para modo local/on-premise |

---

## 🔑 Credenciales por Entorno

| Entorno | URL | Usuario | Password | Rol |
|---------|-----|---------|----------|-----|
| Desarrollo | localhost:8000 | admin@iso27001.local | admin123 | SUPERADMIN |
| QA (Nube) | iso27001-qa.onrender.com | admin@iso27001.local | admin123 | SUPERADMIN |
| Prod (Nube) | iso27001-prod.onrender.com | admin@iso27001.local | admin123 | SUPERADMIN |

---

*Documento actualizado: 2026-03-31 - Modo C (QA) reactivado*