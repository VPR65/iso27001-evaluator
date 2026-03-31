# 🧪 PLAN DE PRUEBAS FUNCIONALES COMPLETO - ISO 27001 Evaluator

**Versión:** 2.0.0  
**Fecha:** 2026-03-31  
**Estado:** EN REVISIÓN - Pruebas insuficientes detectadas

---

## 📋 RESUMEN EJECUTIVO

### Problema Identificado
Las pruebas actuales NO detectan:
- ❌ Errores de UX (páginas en blanco, JSON plano)
- ❌ Errores en operaciones CRUD
- ❌ Validaciones de formularios
- ❌ Redirecciones incorrectas
- ❌ Estados de respuesta HTTP incorrectos

### Acción Requerida
Crear suite de pruebas **100% exhaustiva** que cubra todos los flujos críticos del sistema.

---

## 🎯 CATEGORÍAS DE PRUEBA (8 ÁREAS)

### 1. AUTENTICACIÓN (15+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 1.1 | Login con credenciales válidas | POST /login | Redirección a dashboard |
| 1.2 | Login con password incorrecto | POST /login | Error "Credenciales inválidas" |
| 1.3 | Login con email no registrado | POST /login | Error "Credenciales inválidas" |
| 1.4 | Login con email vacío | POST /login | Error campo requerido |
| 1.5 | Login con password vacío | POST /login | Error campo requerido |
| 1.6 | Logout exitoso | POST /logout | Redirección a login |
| 1.7 | Acceso a dashboard sin login | GET /dashboard | Redirección a login |
| 1.8 | Sesión expirada | Cookie expirada | Redirección a login |
| 1.9 | Login con 2FA habilitado | POST /login | Redirección a verify-2fa |
| 1.10 | Código 2FA incorrecto | POST /verify-2fa | Error "Código inválido" |
| 1.11 | CSRF protection en login | Sin token CSRF | Error 403 |
| 1.12 | SQL Injection en login | `' OR '1'='1` | Error o sanitizado |
| 1.13 | XSS en email login | `<script>alert(1)</script>` | Sanitizado |
| 1.14 | Login con email muy largo | 500+ caracteres | Error o truncado |
| 1.15 | Múltiples intentos fallidos | 5+ intentos | Rate limiting |

---

### 2. DASHBOARD (10+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 2.1 | Dashboard como superadmin | GET /dashboard | 200 + datos completos |
| 2.2 | Dashboard como evaluador | GET /dashboard | 200 + datos limitados |
| 2.3 | Dashboard como admin_cliente | GET /dashboard | 200 + solo su cliente |
| 2.4 | KPI cards cargan | GET /dashboard | KPIs visibles |
| 2.5 | Gráficos cargan | GET /dashboard | Charts renderizados |
| 2.6 | Sidebar muestra según rol | GET /dashboard | Menú correcto |
| 2.7 | Fecha/hora actual | GET /dashboard | Hora correcta |
| 2.8 | Dashboard sin datos | GET /dashboard | Mensaje "sin datos" |
| 2.9 | Dashboard con много外语 | GET /dashboard | Caracteres correctos |
| 2.10 | timeout de sesión en dashboard | Sesión expirada | Redirección a login |

---

### 3. EVALUACIONES (20+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 3.1 | Listar evaluaciones | GET /evaluations | 200 + lista |
| 3.2 | Crear evaluación válida | POST /evaluations | 302 + creada |
| 3.3 | Crear sin nombre | POST /evaluations | Error validación |
| 3.4 | Crear sin cliente | POST /evaluations | Error validación |
| 3.5 | Ver evaluación específica | GET /evaluations/{id} | 200 + detalles |
| 3.6 | Evaluación inexistente | GET /evaluations/{id} | 404 |
| 3.7 | Editar evaluación | POST /evaluations/{id}/edit | 302 |
| 3.8 | Editar sin permisos | POST /evaluations/{id}/edit | 403 |
| 3.9 | Responder control | POST /evaluate/{id} | 200 + respuesta guardada |
| 3.10 | Responder sin evidencia | POST /evaluate/{id} | Advertencia o allowed |
| 3.11 | Subir evidencia válida | POST /evaluate/{id} | 200 + archivo guardado |
| 3.12 | Subir archivo no permitido | POST /evaluate/{id} | Error tipo archivo |
| 3.13 | Subir archivo muy grande | POST /evaluate/{id} | Error tamaño |
| 3.14 | Eliminar evaluación | POST /evaluations/{id}/delete | 200 + JSON {success: true} |
| 3.15 | Eliminar con password wrong | POST /evaluations/{id}/delete | 400 + error en JSON |
| 3.16 | Eliminar sin CSRF | POST /evaluations/{id}/delete | 403 |
| 3.17 | Eliminar sin ser superadmin | POST /evaluations/{id}/delete | 401 |
| 3.18 | Evaluación de otro cliente | GET /evaluations/{id} | 403 o 404 |
| 3.19 | Progreso se calcula bien | GET /evaluations | Porcentaje correcto |
| 3.20 | Filtrar por cliente | GET /evaluations?client_id=... | Filtro aplicado |

---

### 4. ADMIN - CLIENTES (15+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 4.1 | Listar clientes (superadmin) | GET /admin/clients | 200 + lista completa |
| 4.2 | Listar clientes (evaluador) | GET /admin/clients | 403 |
| 4.3 | Crear cliente válido | POST /admin/clients | 302 + creado |
| 4.4 | Crear cliente sin nombre | POST /admin/clients | Error validación |
| 4.5 | Crear cliente con email duplicado | POST /admin/clients | Error "ya existe" |
| 4.6 | Editar cliente | POST /admin/clients/{id}/edit | 302 |
| 4.7 | Eliminar cliente con datos | POST /admin/clients/{id}/delete | Confirmación o error si tiene datos |
| 4.8 | Eliminar cliente inexistente | POST /admin/clients/{id}/delete | 404 |
| 4.9 | Ver detalles cliente | GET /admin/clients/{id} | 200 + detalles |
| 4.10 | Ver clientes con filtros | GET /admin/clients?search=... | Filtro aplicado |
| 4.11 | Pagination clientes | GET /admin/clients?page=2 | Página correcta |
| 4.12 | Ordenar por nombre | GET /admin/clients?sort=name | Orden correcto |
| 4.13 | Cliente con usuarios asociados | GET /admin/clients/{id} | Muestra usuarios |
| 4.14 | Cliente con evaluaciones asociadas | GET /admin/clients/{id} | Muestra evaluaciones |
| 4.15 | CSRF en operaciones admin | Sin token | 403 |

---

### 5. ADMIN - USUARIOS (15+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 5.1 | Listar usuarios (superadmin) | GET /admin/all-users | 200 + lista completa |
| 5.2 | Crear usuario válido | POST /admin/users | 302 + creado |
| 5.3 | Crear sin email | POST /admin/users | Error validación |
| 5.4 | Crear con email inválido | POST /admin/users | Error formato email |
| 5.5 | Crear sin password | POST /admin/users | Error validación |
| 5.6 | Crear con password débil | POST /admin/users | Error "password débil" |
| 5.7 | Editar usuario | POST /admin/users/{id}/edit | 302 |
| 5.8 | Editar rol de usuario | POST /admin/users/{id}/edit | Cambio de rol |
| 5.9 | Eliminar usuario | POST /admin/users/{id}/delete | 200 + JSON |
| 5.10 | Eliminar último superadmin | POST /admin/users/{id}/delete | Error "no puedes" |
| 5.11 | Asignar usuario a cliente | POST /admin/users | Cliente asignado |
| 5.12 | Ver usuarios por cliente | GET /admin/users?client_id=... | Filtrado |
| 5.13 | Cambiar password desde admin | POST /admin/users/{id}/change-password | 200 |
| 5.14 | Usuario activo/inactivo | POST /admin/users/{id}/toggle-active | Cambio de estado |
| 5.15 | Datos sensibles sanitizados | GET /admin/users | Passwords no visibles |

---

### 6. DOCUMENTOS (12+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 6.1 | Listar documentos | GET /documents | 200 + lista |
| 6.2 | Subir documento válido | POST /documents | 302 + subido |
| 6.3 | Subir documento sin título | POST /documents | Error validación |
| 6.4 | Descargar documento | GET /documents/{id}/download | 200 + archivo |
| 6.5 | Ver documento | GET /documents/{id} | 200 + preview |
| 6.6 | Eliminar documento | POST /documents/{id}/delete | 200 |
| 6.7 | Documento de otro cliente | GET /documents/{id} | 403 |
| 6.8 | Versiones de documento | GET /documents/{id}/versions | Lista versiones |
| 6.9 | Publicar documento | POST /documents/{id}/publish | 200 |
| 6.10 | Buscar documentos | GET /documents?search=... | Resultados |
| 6.11 | Filtrar por tipo | GET /documents?type=... | Filtro |
| 6.12 | Permisos de descarga | GET /documents/{id}/download | Según rol |

---

### 7. API - AI (10+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 7.1 | Estado de IA | GET /api/ai/status | 200 + estado |
| 7.2 | Listar modelos disponibles | GET /api/ai/models | 200 + lista modelos |
| 7.3 | Cambiar modelo | POST /api/ai/set-model | 200 + modelo cambiado |
| 7.4 | Analizar con IA | POST /api/ai/analyze | 200 + análisis |
| 7.5 | IA no disponible | POST /api/ai/analyze | Fallback o error manejo |
| 7.6 | Timeout de IA | POST /api/ai/analyze | Timeout handling |
| 7.7 | API key inválida | POST /api/ai/analyze | Error clear |
| 7.8 | Sin permisos para IA | POST /api/ai/analyze | 403 |
| 7.9 | Rate limiting API | Múltiples requests | 429 Too Many |
| 7.10 | Caching de respuestas | Mismo request | Respuesta cacheada |

---

### 8. PAGINAS DE ERROR (5+ tests)
| # | Test Case | Método | Esperado |
|---|-----------|--------|----------|
| 8.1 | Página 404 personalizada | GET /pagina-inexistente | 200 + página diseñada |
| 8.2 | Error 500 personalizado | Forzar error | 200 + página diseñada |
| 8.3 | Error 403 personalizado | Acceso denegado | 200 + página diseñada |
| 8.4 | Mantener diseño en errores | Cualquier error | Mismo header/sidebar |
| 8.5 | Links útiles en errores | Error pages | Links a páginas válidas |

---

## 📊 COBERTURA TOTAL: 100+ TESTS

| Categoría | Tests |
|-----------|-------|
| Autenticación | 15 |
| Dashboard | 10 |
| Evaluaciones | 20 |
| Admin - Clientes | 15 |
| Admin - Usuarios | 15 |
| Documentos | 12 |
| API - AI | 10 |
| Páginas de Error | 5 |
| **TOTAL** | **102** |

---

## 🚀 IMPLEMENTACIÓN

### Paso 1: Crear script de pruebas completo
- Nombre: `scripts/comprehensive_test.py`
- Debe ejecutar TODOS los 100+ casos
- Reporte detallado de resultados

### Paso 2: Ejecutar en orden
1. Primero en local (desarrollo)
2. Luego en QA (Render)
3. Documentar resultados

### Paso 3: Automatizar en CI/CD
- GitHub Actions ejecuta tests en cada push
- Bloquea merge si tests fallan

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear `scripts/comprehensive_test.py`
- [ ] Implementar 102 test cases
- [ ] Ejecutar en desarrollo
- [ ] Ejecutar en QA (Render)
- [ ] Corregir errores encontrados
- [ ] Automatizar en GitHub Actions
- [ ] Documentar resultados

---

*Documento creado: 2026-03-31*  
*Próximo paso: Implementar comprehensive_test.py*