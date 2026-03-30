# 🐳 Guía de Despliegue con Docker

## 📋 Descripción

Este documento describe cómo desplegar el **ISO 27001 & ITIL Evaluator** usando Docker Compose, con soporte completo para IA local (Ollama) y base de datos PostgreSQL.

---

## 🚀 Requisitos Previos

- Docker Desktop (Windows/Mac) o Docker Engine (Linux)
- Docker Compose v2.0+
- 5 GB de espacio en disco
- 4 GB RAM mínimo (8 GB recomendado)

---

## 🎯 Opciones de Despliegue

### Opción 1: Docker con IA Local (Recomendado)

Despliega la aplicación completa con Ollama para IA local:

```bash
# 1. Clonar o copiar archivos al servidor
# 2. Configurar variables de ambiente
cp .env.docker .env
# Editar .env y cambiar SECRET_KEY y DB_PASSWORD

# 3. Iniciar todos los servicios (incluye Ollama)
docker-compose up -d --profile ollama

# 4. Verificar estado
docker-compose ps

# 5. Ver logs
docker-compose logs -f
```

### Opción 2: Docker sin IA (Solo App + DB)

```bash
# Iniciar sin Ollama
docker-compose up -d

# La app funcionará en modo "Sin IA" hasta que se configure Ollama externo
```

---

## 🔧 Configuración

### Variables de Ambiente (.env)

```bash
# Copiar archivo de ejemplo
cp .env.docker .env

# Editar con valores de producción
nano .env  # o tu editor favorito
```

**Variables Críticas:**
- `SECRET_KEY`: Generar aleatoria para producción
- `DB_PASSWORD`: Contraseña segura para PostgreSQL
- `NVIDIA_API_KEY`: (Opcional) Para fallback a NVIDIA NIM

### Puertos Utilizados

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| App | 8000 | Aplicación web |
| DB | 5432 | PostgreSQL |
| Ollama | 11434 | IA local (opcional) |

---

## 📦 Comandos Comunes

### Iniciar servicios

```bash
# Todos los servicios (con IA)
docker-compose up -d --profile ollama

# Solo App y DB (sin IA)
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f ollama
```

### Detener servicios

```bash
# Detener todo
docker-compose down

# Detener pero mantener volúmenes (datos)
docker-compose down --volumes
```

### Ver estado

```bash
# Estado de servicios
docker-compose ps

# Uso de recursos
docker stats
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart app
```

---

## 🔍 Solución de Problemas

### Problema 1: "Puerto ya en uso"

```bash
# Cambiar puertos en .env
APP_PORT=8001
DB_PORT=5433
OLLAMA_PORT=11435
```

### Problema 2: "Ollama no inicia"

```bash
# Ver logs de Ollama
docker-compose logs ollama

# Reiniciar Ollama
docker-compose restart ollama

# Verificar que Ollama responde
curl http://localhost:11434/api/tags
```

### Problema 3: "Base de datos no conecta"

```bash
# Verificar health de DB
docker-compose ps db

# Ver logs de DB
docker-compose logs db

# Reiniciar DB
docker-compose restart db
```

### Problema 4: "La app no responde"

```bash
# Verificar health check
curl http://localhost:8000/health

# Ver logs de la app
docker-compose logs app

# Reiniciar app
docker-compose restart app
```

---

## 📊 Volúmenes y Persistencia

### Volúmenes Creados

| Volumen | Contenido | Ubicación |
|---------|-----------|-----------|
| `postgres_data` | Base de datos PostgreSQL | `/var/lib/postgresql/data` |
| `ollama_models` | Modelos de Ollama | `/root/.ollama/models` |
| `app_uploads` | Evidencias subidas | `/app/uploads` |
| `app_backups` | Backups | `/app/backups` |

### Backup de Volúmenes

```bash
# Backup de PostgreSQL
docker-compose exec db pg_dump -U iso27001 iso27001 > backup.sql

# Backup de Ollama models
docker run --rm -v iso27001_ollama_models:/source -v $(pwd):/backup alpine tar czf /backup/ollama_models.tar.gz -C /source .

# Backup de uploads
docker run --rm -v iso27001_uploads:/source -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /source .
```

---

## 🔐 Seguridad

### Para Producción:

1. ✅ Cambiar `SECRET_KEY` por una aleatoria
2. ✅ Cambiar `DB_PASSWORD` por una segura
3. ✅ Usar red privada (Docker network)
4. ✅ Configurar firewall para puertos
5. ✅ Actualizar Docker regularmente
6. ✅ Revisar logs de seguridad

### Generar SECRET_KEY:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32

# Linux
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

---

## 📈 Monitoreo

### Ver logs en tiempo real

```bash
docker-compose logs -f
```

### Ver métricas de recursos

```bash
docker stats
```

### Ver logs específicos

```bash
# App
docker-compose logs -f app

# DB
docker-compose logs -f db

# Ollama
docker-compose logs -f ollama
```

---

## 🚀 Próximos Pasos (Roadmap)

- [ ] Scripts de backup automático
- [ ] Monitoreo con Prometheus/Grafana
- [ ] Auto-escalado
- [ ] Load balancing
- [ ] Alta disponibilidad

---

## 📞 Soporte

Para más información:
- `docs/PROJECT_STATUS.md` - Estado del proyecto
- `docs/DEPLOYMENT_AND_TESTING.md` - Guía de deploy
- `docs/OLLAMA_START_STOP.md` - Gestión de Ollama

---

**Última actualización:** 2026-03-30  
**Versión:** v1.7.4  
**Docker Compose:** v3.8  
**PostgreSQL:** 15-alpine  
**Ollama:** latest
