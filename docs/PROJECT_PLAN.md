# PLAN DE PROYECTO - ISO 27001 Evaluator

> Version: 1.1.0 | Ultima actualizacion: 2026-03-22

---

## 1. INFORMACION GENERAL

| Campo              | Valor                                                     |
|--------------------|------------------------------------------------------------|
| Nombre             | ISO 27001 Evaluator                                       |
| Version actual     | v1.1.0                                                    |
| Proposito          | Sistema web para evaluar cumplimiento ISO 27001:2022        |
| Metodologia        | ITIL v4 + Agile Scrum                                      |
| Alcance            | Multi-tenant, 93 controles ISO 27001, multi-idioma       |
| Tecnologias        | FastAPI, SQLModel, PostgreSQL, Jinja2, HTMX, Chart.js         |
| Autor              | Equipo de Desarrollo                                       |
| Fecha de inicio    | 2026-03-22                                               |

---

## 2. JUSTIFICACION DEL PROYECTO

Las organizaciones necesitan evaluar periodicamente su postura de seguridad de la informacion bajo el marco ISO 27001:2022. Este sistema permite:

- **Automatizar** la evaluacion de los 93 controles del Anexo A
- **Medir** la madurez con el modelo CMMI (0-5)
- **Gestionar** cambios y remediaciones con RFCs ITIL
- **Documentar** politicas y controles con versionado semantico
- **Visualizar** el avance con estadisticas y graficos
- **Importar/Exportar** datos desde/hacia Excel

---

## 3. ALCANCE DEL PROYECTO

### 3.1 Funcionalidades Incluidas

| Modulo              | Funcionalidades                                         |
|---------------------|--------------------------------------------------------|
| Evaluaciones        | Crear, evaluar, completar evaluaciones ISO 27001        |
| Dashboard           | KPIs, score de madurez, reloj en tiempo real           |
| Documentos          | CRUD, versionado semver, diff, rollback, aprobacion  |
| RFCs                | Solicitudes de cambio ITIL, 4 niveles de riesgo         |
| Sprints             | Backlog, sprints, tareas vinculadas a controles         |
| Import/Export       | Integracion con Excel (openpyxl + pandas)               |
| Gestion de usuarios | 4 roles, autenticacion, audit log                       |
| Multi-tenant        | Clientes separados con datos aislados                    |

### 3.2 Funcionalidades Excluidas (Fase 1)

- Autenticacion via SSO/OAuth
- Notificaciones por email
- Integracion con sistemas externos (SIEM, ticketing)
- Despliegue en la nube (AWS/GCP/Azure)
- Tests automatizados unitarios

---

## 4. ESTRUCTURA DE DOMINIOS ISO 27001:2022

| Dominio                            | Controles | Descripcion                           |
|------------------------------------|-----------|---------------------------------------|
| A.5 Controles Organizacionales     | 37        | Politicas, roles, contacto, proyectos |
| A.6 Controles de Personas          | 8         | Screening, terminos, formacion         |
| A.7 Controles Fisicos              | 14        | Perimetro, acceso, entorno, equipos    |
| A.8 Controles Tecnologicos         | 34        | Acceso, criptografia, redes, desarrollo|
| **TOTAL**                          | **93**    | Anexo A completo ISO 27001:2022        |

---

## 5. MODELO DE MADUREZ CMMI

| Nivel | Nombre         | Descripcion                                                   |
|-------|----------------|----------------------------------------------------------------|
| 0     | No existe      | No hay evidencia ni proceso implementado                        |
| 1     | Inicial        | Proceso ad-hoc, dependiente de personas                         |
| 2     | Gestionado     | Proceso documentado y repetible                                |
| 3     | Definido       | Proceso estandarizado y optimizado                            |
| 4     | Cuantitativamente gestionado | Proceso medido y controlado estadisticamente |
| 5     | Optimizado    | Mejora continua basada en metricas                             |

---

## 6. ROLES DEL SISTEMA

| Rol              | Responsabilidades                                         |
|------------------|---------------------------------------------------------|
| Superadmin       | Gestiona todo: clientes, usuarios, configuraciones       |
| Admin Cliente    | Gestiona su cliente, evaluaciones, usuarios del cliente  |
| Evaluador        | Evalua controles, sube evidencia, crea RFCs              |
| Solo Vista       | Solo puede ver resultados (sin modificacion)              |

---

## 7. ROLES ITIL DEL EQUIPO DE DESARROLLO

| Rol ITIL              | Persona asignada | Responsabilidad                         |
|-----------------------|------------------|-----------------------------------------|
| Service Request Mgmt   | Admin            | Recibe y clasifica solicitudes de cambio |
| Change Manager        | Dev Lead         | Evalua y aprueba/rechaza RFCs           |
| Release Manager       | Dev Lead         | Despliega cambios a produccion          |
| Incident Manager      | Dev Team         | Resuelve incidentes en el sistema       |
| Problem Manager       | Dev Lead         | Analiza causas raiz de problemas        |
| Service Desk          | Dev Team         | Soporte de primer nivel                 |

---

## 8. GESTION DEL CAMBIO (RFC)

Todo cambio en el codigo sigue este proceso:

1. **Solicitud (RFC)** - Se crea en el sistema con descripcion y nivel de riesgo
2. **Evaluacion** - Se evalua impacto, costo y riesgo
3. **Aprobacion** - Segun nivel de riesgo (ver tabla abajo)
4. **Implementacion** - Se desarrolla en rama feature/
5. **Pruebas** - Se verifica en entorno local
6. **Despliegue** - Se sube a produccion
7. **Revision post-cambio** - Se documentan lecciones aprendidas

| Nivel de riesgo | Impacto                    | Aprobacion requerida        |
|-----------------|----------------------------|----------------------------|
| Critico (P1)    | Sistema caido, fuga datos  | Cambios inmediatos, informar luego |
| Alto (P2)       | Funcionalidad afectada      | Change Manager + Dev Lead  |
| Medio (P3)      | Impacto parcial             | Dev Lead                   |
| Bajo (P4)        | Cambios menores, cosmeticas | Auto-aprobado              |

---

## 9. ROADMAP

### Fase 1 - Fundacion (Completada v1.0.0 - v1.1.0)
- [x] Arquitectura base FastAPI + PostgreSQL
- [x] Autenticacion y autorizacion (4 roles)
- [x] 93 controles ISO 27001:2022 seedeados
- [x] Evaluaciones con madurez CMMI
- [x] Dashboard con estadisticas
- [x] RFCs ITIL
- [x] Documentos con versionado
- [x] Sprints agiles
- [x] Import/Export Excel
- [x] UI moderna (sidebar, reloj, iconos)
- [x] Audit log

### Fase 2 - Produccion (v1.2.0 - v1.3.0)
- [ ] Despliegue en servidor de produccion
- [ ] Docker + docker-compose configurado
- [ ] Backup automatico diario
- [ ] SSL/TLS (Let's Encrypt)
- [ ] Documentacion completa (este archivo)
- [ ] QA completo de todos los modulos

### Fase 3 - Mejoras (v1.4.0 - v1.5.0)
- [ ] Notificaciones por email
- [ ] Dashboard ejecutivo imprimible (PDF)
- [ ] Matriz de riesgos integrada
- [ ] Alertas de controles criticos vencidos

### Fase 4 - Escalabilidad (v2.0.0)
- [ ] Migracion a PostgreSQL
- [ ] Autenticacion SSO/OAuth
- [ ] API REST publica
- [ ] Multi-idioma (espanol/ingles)

---

## 10. CRONOGRAMA ESTIMADO

| Fase       | Duracion estimada | Entregables              |
|------------|-------------------|---------------------------|
| Fase 1     | 2 dias            | Sistema funcional base     |
| Fase 2     | 1 semana          | Produccion lista          |
| Fase 3     | 2 semanas         | Mejoras y optimizaciones   |
| Fase 4     | 1 mes             | Escalabilidad y API       |

---

## 11. GESTION DE RIESGOS

| Riesgo                      | Probabilidad | Impacto | Mitigacion                                |
|-----------------------------|--------------|---------|--------------------------------------------|
| Perdida de datos            | Baja         | Critico | Backup diario automatico + rollback        |
| Inyeccion SQL/XSS          | Media        | Critico | ORM SQLModel, sanitizacion de inputs      |
| Credenciales expuestas      | Baja         | Critico | Variables de entorno, nunca hardcodear    |
| Dependencias obsoletas      | Media        | Medio   | pip-compile, actualizar periodicamente     |
| Sobrecarga del servidor     | Baja         | Medio   | Monitoreo de recursos, caching             |
| Auditoria no conforme        | Baja         | Alto    | Audit log completo, registros inmutables   |

---

## 12. COMUNICACION Y REPORTES

| Tipo de reporte            | Frecuencia      | Destinatarios              |
|----------------------------|-----------------|----------------------------|
|Estado del proyecto          | Semanal         | Sponsor, equipo            |
|Incidentes de seguridad      | Inmediato       | Change Manager, equipo     |
|Metricas de evaluacion      | Mensual         | Gerencia, auditores        |
|Liberaciones/despliegues    | Por release     | Equipo, usuarios clave     |

---

## 13. APROBACIONES

| Role                | Nombre              | Fecha       |
|---------------------|---------------------|-------------|
| Project Sponsor     |                     |             |
| Change Manager      |                     |             |
| Quality Assurance   |                     |             |
| Security Lead       |                     |             |
