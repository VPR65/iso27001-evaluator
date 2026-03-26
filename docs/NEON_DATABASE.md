# MANUAL DE BASE DE DATOS - Neon PostgreSQL

> Fecha: 2026-03-25 | Version: 1.0.0

---

## 1. INFORMACION DE CONEXION

### Datos del proyecto en Neon.tech

| Campo | Valor |
|-------|-------|
| Proyecto | ISO27001-QA |
| Region | Sao Paulo (sa-east-1) |
| Proveedor Cloud | AWS |
| Version PostgreSQL | 17 |
| Almacenamiento | 0.5 GB (Free Tier) |

### Connection String (PRIVADO - NO COMPARTIR)

```
postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Partes del Connection String

| Parte | Valor |
|-------|-------|
| Usuario | `neondb_owner` |
| Password | `npg_PhU0gVlXJ5yW` |
| Host | `ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech` |
| Puerto | 5432 (default) |
| Base de datos | `neondb` |
| Parametros extra | `sslmode=require&channel_binding=require` |

---

## 2. CONFIGURACION EN RENDER

### Variables de Entorno (Environment Variables)

Para que la aplicacion use Neon PostgreSQL en lugar de PostgreSQL local:

1. Ir a Render Dashboard: https://dashboard.render.com
2. Seleccionar el servicio (`iso27001-qa` o `iso27001-prod`)
3. Ir a **Environment** > **Environment Variables**
4. Agregar:

| Name | Value |
|------|-------|
| DATABASE_URL | `postgresql://neondb_owner:***@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require` |

**NOTA:** La aplicacion automaticamente detecta la URL de Neon y configura PostgreSQL correctamente.

---

## 3. VERIFICAR CONEXION

### Desde tu PC (usando psql o Python)

```bash
# Instalar psycopg2 si no esta
pip install psycopg2-binary

# Probar conexion con Python
python
>>> import psycopg2
>>> conn = psycopg2.connect(
...     host="ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech",
...     database="neondb",
...     user="neondb_owner",
...     password="npg_PhU0gVlXJ5yW",
...     sslmode="require"
... )
>>> print("Conexion exitosa!")
>>> conn.close()
```

### Verificar tablas existentes

```python
python
>>> from sqlalchemy import create_engine, inspect
>>> engine = create_engine("postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require")
>>> inspector = inspect(engine)
>>> print(inspector.get_table_names())
```

---

## 4. ESTRUCTURA DE TABLAS

La aplicacion crea automaticamente estas tablas:

| Tabla | Descripcion |
|-------|-------------|
| `client` | Clientes de la empresa |
| `user` | Usuarios del sistema |
| `session` | Sesiones activas |
| `norma` | Normas disponibles (ISO 27001, 9001, etc.) |
| `evaluation` | Evaluaciones creadas |
| `control_definition` | Definiciones de controles ISO |
| `control_response` | Respuestas de cada control |
| `audit_log` | Log de auditoria |
| `document` | Documentos cargados |
| `document_version` | Versiones de documentos |
| `rfc` | Requests for Change (RFCs ITIL) |
| `sprint` | Sprints agiles |
| `sprint_task` | Tareas dentro de sprints |
| `biblioteca_document` | Documentos de la biblioteca |

---

## 5. MANTENER NEON SEGURO

### NO hacer esto:
- ❌ Subir el connection string a GitHub
- ❌ Compartir el password `npg_PhU0gVlXJ5yW`
- ❌ Hacer publik el repositorio si tiene el string

### SI hacer esto:
- ✅ Usar variables de entorno en Render
- ✅ Usar el token de solo lectura si es posible
- ✅ Revocar credenciales si fueron comprometidas

---

## 6. LIMITE DE ALMACENAMIENTO

### Free Tier: 0.5 GB

**Suficiente para:**
- 5 clientes
- 10 usuarios
- 153 controles ISO
- 100+ evaluaciones
- 6 meses de logs de auditoria
- Documentos pequenos (evidencias)

**NO suficiente para:**
- Archivos grandes subidos
- Miles de evaluaciones
- Datos de anos

### Monitorear uso

1. Ir a https://neon.tech
2. Dashboard del proyecto
3. Ver "Storage used" en el panel

---

## 7. BACKUP Y RECUPERACION

### Backups automaticos de Neon

Neon hace automaticamente:
- **Daily backups** retenidos por 7 dias
- **Point-in-time recovery** disponible

### Recuperar desde backup

1. Ir a Neon Dashboard
2. Seleccionar Branch (ej: `main`)
3. Ir a **Backups**
4. Seleccionar punto de restauracion
5. Crear nuevo branch o restaurar sobre existente

### Backup manual

```bash
# Exportar datos (requiere psql o pg_dump)
pg_dump -h ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech \
        -U neondb_owner \
        -d neondb \
        -F c \
        -f backup.dump
```

---

## 8. CAMBIAR PASSWORD

### Desde Neon Dashboard:

1. Ir a https://console.neon.tech
2. Proyecto > **Branches**
3. Seleccionar branch `main`
4. **Roles** > `neondb_owner`
5. **Reset password**
6. Copiar el nuevo password
7. **Actualizar** en Render Environment Variables

---

## 9. CONTACTOS Y RECURSOS

| Recurso | URL |
|---------|-----|
| Neon Dashboard | https://console.neon.tech |
| Documentacion Neon | https://neon.tech/docs |
| Pricing | https://neon.tech/pricing |
| Soporte | https://neon.tech/support |

---

## 10. TROUBLESHOOTING

### Error: "connection refused"
- Verificar que el firewall permite conexiones al puerto 5432
- Verificar que el endpoint es correcto

### Error: "too many connections"
- Reducir `pool_size` en `database.py`
- El free tier tiene limite de conexiones simultaneas

### Error: "database does not exist"
- Verificar que `neondb` es el nombre correcto
- Crear la base si no existe desde Neon Dashboard

### Error: "SSL required"
- Agregar `?sslmode=require` al connection string

---

*Documento creado para referencia. Mantener actualizado cuando cambie la configuracion.*
