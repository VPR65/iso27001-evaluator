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

## 📝 Notas

- Los errores ahora se muestran en ventanas de alerta del navegador
- La experiencia de usuario es consistente con el resto del proyecto

---

*Documento actualizado: 2026-03-31 - v2.0.1*