# 📋 ISSUES PENDIENTES - ISO 27001 Evaluator

**Fecha:** 2026-03-31  
**Versión:** v2.0.1

---

## 🔴 Issues por Corregir

*No hay issues pendientes en esta versión*

---

## ✅ Issues Resueltos

### Issue #1: Delete Operations - Errores en texto plano ✅ CORREGIDO

**Descripción:** Los endpoints de delete (evaluation, user, client) devolvían errores como JSON plano en lugar de seguir el diseño visual del proyecto.

**Ubicación:** 
- `app/routes/admin.py:264-325`
- `app/templates/admin/evaluations.html`
- `app/templates/admin/users.html`
- `app/templates/admin/clients.html`

**Solución implementada:**
1. Cambiado de submit de formulario a fetch AJAX
2. Ahora el JavaScript maneja la respuesta y muestra alertas con el diseño del proyecto
3. Feedback visual consistente (alert) en lugar de página en blanco

**Cambios:**
- evaluations.html: confirmDeleteEval() ahora usa fetch API
- users.html: confirmDeleteUser() ahora usa fetch API
- clients.html: confirmDelete() ahora usa fetch API

**Estado:** ✅ Resuelto en v2.0.1

---

## 📝 Notas de QA

- Las pruebas exhaustivas detectaron 10 problemas (32.3% de 31 tests)
- 9 problemas son de UX (JSON en lugar de páginas HTML)
- 1 problema es endpoint faltante (/api/ai/models requiere auth)
- Dashboard, evaluaciones, documentos y admin clientes funcionan 100%

**Reporte:** `logs/QA_REPORT_20260331.md` y `logs/comprehensive_test_20260331_110717.json`

---

*Documento actualizado: 2026-03-31 - v2.0.1*