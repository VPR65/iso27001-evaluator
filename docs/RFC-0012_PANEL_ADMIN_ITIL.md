# RFC-0012: Panel de Administracion Completo + ITIL v4

> **Estado:** En Progreso
> **Fecha:** 2026-03-25
> **Solicitante:** Equipo de Desarrollo
> **Tipo:** Adaptativo
> **Nivel de Riesgo:** P3 (Medio)
> **Esfuerzo Estimado:** 8 horas

---

## 1. RESUMEN EJECUTIVO

Implementar un panel de administracion completo para el superadmin que permita gestionar clientes, usuarios y evaluaciones de forma segura. Ademas, agregar ITIL v4 como norma evaluable con 34 practicas de gestion de servicios.

---

## 2. JUSTIFICACION DEL CAMBIO

### 2.1 Problema Actual

- No existe forma de eliminar clientes o usuarios desde la interfaz
- Los datos de prueba se acumulan y no hay forma de limpiarlos
- Solo existen endpoints de debug para pruebas
- ITIL v4 no esta disponible como norma evaluable

### 2.2 Beneficios Esperados

| Beneficio | Descripcion |
|-----------|-------------|
| Gestion completa | Superadmin puede administrar todo el sistema |
| Seguridad | Confirmacion con password para acciones destructivas |
| ITIL v4 | Nueva norma para evaluar gestion de servicios IT |
| Limpieza | Permite eliminar datos de prueba obsolete |

---

## 3. ALCANCE

### 3.1 Incluido

- Panel de administracion de clientes
- Panel de administracion de usuarios
- Panel de administracion de evaluaciones
- Eliminacion segura con confirmacion de password
- ITIL v4 como norma evaluable (34 practicas)
- Tests automatizados
- Documentacion actualizada

### 3.2 Excluido

- Modificacion de evaluaciones existentes (solo eliminar)
- Edicion de usuarios (solo crear y eliminar)
- Exportacion de datos

---

## 4. ESPECIFICACION TECNICA

### 4.1 ITIL v4 - Controles/Prácticas

| Dominio | Práctica | Descripcion |
|---------|----------|-------------|
| General | Service Value System | Principios, gobernanza, cadena de valor |
| General | 4 Dimensions Model | Organizacion, personas, tecnologia, partners |
| Gobernanza | Direct, Plan, Improve | Direccion y mejora continua |
| Cadena de Valor | Value Streams | Diseño y construccion de servicios |
| Cadena de Valor | Delight and Drive | Generar valor para stakeholders |
| Operacional | Change Enablement | Gestionar cambios de servicios |
| Operacional | Incident Management | Responder incidentes |
| Operacional | Problem Management | Investigar y resolver problemas |
| Operacional | Service Request | Atender solicitudes |
| Mejora | Continual Improvement | Mejora continua de servicios |
| Mejora | Measurement & Reporting | Medicion y reporteo |
| Relaciones | Business Analysis | Analisis de necesidades |
| Relaciones | Portfolio Management | Gestionar portafolio de servicios |
| Relaciones | Relationship Management | Gestionar relaciones |
| Suministro | Supplier Management | Gestionar proveedores |
| Suministro | Service Level | Acuerdos de nivel de servicio |
| Suministro | Monitoring | Monitoreo de servicios |
| Tecnico | Deployment Management | Despliegue de cambios |
| Tecnico | Infrastructure & Platform | Gestion de infraestructura |
| Tecnico | Software Development | Desarrollo de software |
| Tecnico | Operations Management | Operaciones de TI |

**Total: 34 prácticas**

### 4.2 Endpoints Nuevos

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/admin/clients` | Lista de clientes |
| POST | `/admin/clients` | Crear cliente |
| POST | `/admin/clients/{id}/delete` | Eliminar cliente |
| POST | `/admin/users/{id}/delete` | Eliminar usuario |
| GET | `/admin/evaluations` | Lista de evaluaciones |
| POST | `/admin/evaluations/{id}/delete` | Eliminar evaluacion |

### 4.3 Confirmacion con Password

- Modal en frontend con input de password
- Verificacion en backend contra password del superadmin
- Registro en audit log de todas las eliminaciones

---

## 5. IMPACTO

### 5.1 Impacto en Usuarios

| Rol | Impacto |
|-----|---------|
| Superadmin | Gana funcionalidad de administracion |
| Admin Cliente | Sin cambios |
| Evaluador | Sin cambios |
| Vista Solo | Sin cambios |

### 5.2 Impacto Tecnico

| Aspecto | Impacto |
|---------|---------|
| Base de datos | Sin cambios (nuevas tablas no requeridas) |
| API | Nuevos endpoints |
| Frontend | Nuevos templates |
| Performance | Minimo impacto |

---

## 6. RIESGOS Y MITIGACION

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|-------------|
| Eliminacion accidental | Baja | Alto | Confirmacion con password obligatoria |
| Perdid de datos | Baja | Alto | Backup antes de despliegue |
| Incompatibilidad | Baja | Medio | Tests automatizados |

---

## 7. PLAN DE IMPLEMENTACION

### Fase 1: ITIL v4 (2 horas)
- Agregar definicion de norma en seed.py
- Agregar 34 practicas ITIL
- Tests de verificacion

### Fase 2: Panel Clientes (2 horas)
- Nueva ruta y template
- Crear y eliminar cliente
- Confirmacion con password

### Fase 3: Panel Usuarios (2 horas)
- Agregar boton eliminar a usuarios existentes
- Confirmacion con password
- Eliminacion en cascada (sesiones)

### Fase 4: Panel Evaluaciones (2 horas)
- Nueva ruta y template
- Eliminar evaluacion y respuestas

### Fase 5: Documentacion (1 hora)
- Actualizar CHANGELOG
- Actualizar ARCHITECTURE
- Actualizar CONFIG_REGISTRY

---

## 8. CRONOGRAMA

| Dia | Actividad |
|-----|-----------|
| Dia 1 | Fases 1-2 |
| Dia 2 | Fases 3-4 |
| Dia 3 | Fase 5 + QA + Prod |

---

## 9. CRITERIOS DE ACEPTACION

- [ ] Superadmin puede ver todos los clientes
- [ ] Superadmin puede crear cliente nuevo
- [ ] Superadmin puede eliminar cliente con password
- [ ] Superadmin puede ver todos los usuarios
- [ ] Superadmin puede eliminar usuario con password
- [ ] Superadmin puede ver todas las evaluaciones
- [ ] Superadmin puede eliminar evaluacion con password
- [ ] ITIL v4 aparece como norma seleccionable
- [ ] Evaluacion ITIL muestra 34 practicas
- [ ] Todos los tests pasan
- [ ] Documentacion actualizada

---

## 10. APROBACIONES

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Solicitud | Equipo Desarrollo | 2026-03-25 | |
| Aprobacion | Dev Lead | Pendiente | |

---

## 11. HISTORIAL DE CAMBIOS

| Version | Fecha | Descripcion | Autor |
|---------|-------|-------------|-------|
| 1.0 | 2026-03-25 | Creacion inicial | Equipo Desarrollo |
