# AGENTS.md — Convenciones de Desarrollo

> **Nota:** Este proyecto hereda skills globales desde `C:\Users\vpalma\.opencode\skills\`. 
> Verificar que las instrucciones de los skills 00-05 se apliquen automáticamente.

## Ramas Git

- `main`: Produccion (solo merge desde release)
- `dev`: Integracion de features
- `feature/nombre`: Una rama por funcionalidad

```bash
git checkout -b feature/mi-feature
git checkout dev && git merge feature/mi-feature
git checkout main && git merge dev
```

## Commits

Usar prefijos en ingles:

```
feat:    nueva funcionalidad
fix:     correccion de bug
security: correccion de vulnerabilidad
refactor: mejora de codigo sin cambio de funcionalidad
docs:    documentacion
backup:  restauracion de datos
config:  cambios de configuracion
deps:    actualizacion de dependencias
```

Ejemplos:
```
feat: agregar evaluacion de controles CMMI con upload de evidencia
fix: corregir paginacion en listado de evaluaciones
security: sanitizar inputs contra XSS en notas de control
backup: restaurar version 1.2.0 del cliente ACME
```

## Tags de Release (Semver)

```
vMAJOR.MINOR.PATCH

  MAJOR: Cambio incompatible en API o arquitectura
  MINOR: Nueva funcionalidad compatible hacia atras
  PATCH: Correccion de bugs compatible hacia atras

Ejemplos:
  v1.0.0  ← Primera version
  v1.1.0  ← Nueva funcionalidad
  v1.1.1  ← Fix de bug
  v2.0.0  ← Nueva arquitectura
```

```bash
git tag v1.0.0 -m "Release v1.0.0"
git push origin --tags
```

## Antes de Cada Despliegue

1. **OBLIGATORIO**: Crear backup antes de cualquier cambio en DB
   ```bash
   python scripts/backup.py backup
   ```

2. Verificar que el codigo compila y la DB responde
   ```bash
   python -c "from app.main import app; print('OK')"
   ```

3. Taggear la version
   ```bash
   git tag vX.Y.Z -m "Mensaje del release"
   ```

4. Desplegar y verificar health check
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   curl http://localhost:8000/health
   ```

## Rollback (1 comando, < 30 segundos)

```bash
python scripts/rollback.py              # Rollback al tag anterior
python scripts/rollback.py v1.2.0       # Rollback a version especifica
python scripts/rollback.py --list        # Ver todos los tags
```

## Backup / Restauracion

```bash
# Backup completo (DB + uploads)
python scripts/backup.py backup

# Backup solo base de datos
python scripts/backup.py backup-db

# Listar backups disponibles
python scripts/backup.py list

# Restaurar desde backup
python scripts/backup.py restore backups/backup_YYYYMMDD.zip
```

## Seguridad (OBLIGATORIO)

- **TODOS** los inputs del usuario deben sanitizarse
- **NO** hacer `eval()` ni `exec()` con input de usuario
- **NO** hardcodear secretos en el codigo (usar variables de entorno)
- **NUNCA** hacer SQL con concatenacion de strings (usar SQLModel/SQLAlchemy ORM)
- **SIEMPRE** verificar permisos en cada endpoint
- Archivos subidos deben validarse por tipo y tamano antes de guardar

## Multi-tenant

- Todos los datos tienen `client_id`
- Cada query debe filtrar por el cliente del usuario autenticado
- Superadmin puede ver todos los clientes
- Los demas roles solo ven su propio `client_id`

## Modelo de Datos (SQLModel)

- Usar `sqlmodel` para todos los modelos
- No usar `declarative_base` de SQLAlchemy directo
- Relaciones con `Relationship` de SQLModel
- Enums para campos con valores fijos

## Autenticacion

- Sesiones basadas en cookies (httponly, samesite=lax)
- Nunca almacenar passwords en texto plano
- Usar `bcrypt` via `passlib`
- Expirar sesiones automaticamente

## Revision de Codigo Checklist

Antes de hacer commit, verificar:
- [ ] No hay secretos hardcodeados
- [ ] Inputs de usuario sanitizados
- [ ] Permisos verificados en el endpoint
- [ ] Backup creado antes de migrar DB
- [ ] Tests basicos funcionan
- [ ] Mensaje de commit con prefijo correcto
- [ ] **Documentacion actualizada** (version y sin referencias obsoletas)
- [ ] **CHANGELOG.md** actualizado con los cambios
- [ ] Ejecutar `python scripts/validate_docs.py` para validar documentacion

## Estructura de Archivos

No cambiar la estructura de carpetas sin discutirlo antes.
Mantener rutas relativas para facilitar el deploy.

## Control de Versiones de Documentacion

Para asegurar que la documentacion este siempre actualizada:

1. **Version sincronizada**: Todos los docs criticols (ARCHITECTURE.md, CONFIG_REGISTRY.md) deben tener la misma version que CHANGELOG.md
2. **Validacion automatica**: Ejecutar `python scripts/validate_docs.py` antes de cada commit
3. **Check de SQLite**: El script valida que no queden referencias obsoletas a SQLite
4. **CHANGELOG primero**: Todo cambio debe registrarse en CHANGELOG.md antes de hacer commit

### Flujo de actualizacion de documentacion

```bash
# 1. Hacer los cambios de codigo
git add app/...

# 2. Actualizar CHANGELOG.md con los cambios

# 3. Actualizar version en docs (si corresponde)
#    - ARCHITECTURE.md
#    - CONFIG_REGISTRY.md
#    - MASTER_DIAGRAM.md

# 4. Validar documentacion
python scripts/validate_docs.py

# 5. Si todo OK, hacer commit
git commit -m "feat: descripcion del cambio"
```

## Referencias de Documentacion

Para referencia completa de procesos y arquitectura, ver:

| Archivo | Referencia rapida |
|---------|------------------|
| `docs/INFRASTRUCTURE.md` | Plataformas gratuitas: tu PC + GitHub + Render |
| `docs/PROCESSES.md` | Flujo Git, RFCs, incidentes, backup, deploy |
| `docs/ARCHITECTURE.md` | Modelo de datos, endpoints, seguridad |
| `docs/TESTING.md` | Plan de QA y checklist de pruebas |
| `docs/CHANGELOG.md` | Registro de cambios por version |
| `docs/PROJECT_PLAN.md` | Roadmap, riesgos, roles ITIL |
