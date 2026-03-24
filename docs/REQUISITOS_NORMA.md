# Guia Estrategica para el Desarrollo de la Herramienta Integral de Evaluacion ISO (9001, 20000-1, 22301, 27001)

> Version: 1.0.0 | Fecha: 2026-03-24

---

## 1. El Nuevo Paradigma de los Sistemas de Gestion: Anexo SL y Ciclo PHVA

La unificacion normativa mediante el **Anexo SL** representa el pilar fundamental de la gobernanza corporativa moderna. Esta Estructura de Alto Nivel (HLS) no es una mera formalidad editorial, sino un marco estrategico que permite a las organizaciones trascender los silos operativos. Al estandarizar terminos, definiciones y la estructura de las clausulas, el Anexo SL facilita la creacion de un **Sistema de Gestion Integrado (IMS)** donde la Calidad, la Seguridad de la Informacion, la Continuidad y los Servicios de TI convergen en una sola estrategia de cumplimiento, eliminando redundancias y optimizando el retorno de inversion en auditoria.

Bajo este esquema, el pensamiento basado en riesgos actua como el tejido conectivo que anticipa desviaciones en las 10 clausulas comunes:

- **Clausulas 1 a 3 (Informativas):** Establecen el alcance, las referencias y el glosario tecnico para evitar ambiguedades.
- **Clausula 4 (Contexto):** Analisis del entorno y partes interesadas. Un cambio critico aqui es la inclusion del **cambio climatico** en las sub-clausulas 4.1 y 4.2.
- **Clausulas 5 a 6 (Liderazgo y Planificacion):** El compromiso de la alta direccion y la definicion de objetivos medibles.
- **Clausula 7 (Apoyo):** Gestion de recursos, competencia y la vital **informacion documentada**.
- **Clausula 8 (Operacion):** La ejecucion tecnica especifica de cada norma.
- **Clausulas 9 a 10 (Evaluacion y Mejora):** El ciclo de cierre mediante auditoria y tratamiento de no conformidades.

---

## 2. Analisis Comparativo de Requisitos Normativos Especificos

| Norma | Enfoque Central | Requisito Operativo Critico |
|-------|-----------------|----------------------------|
| **ISO 9001:2015** | Gestion de la Calidad | Proporcion del servicio y relacion con proveedores externos. |
| **ISO/IEC 20000-1:2018** | Gestion de Servicios de TI | Acuerdos de Nivel de Servicio (SLA) y Catalogo de Servicios. |
| **ISO 22301:2019** | Continuidad del Negocio | Analisis de Impacto en el Negocio (BIA) y Planes de Continuidad. |
| **ISO/IEC 27001:2022** | Seguridad de la Informacion | Declaracion de Aplicabilidad (SoA) y Plan de Tratamiento de Riesgos (RTP). |

### La Transicion Critica de ISO/IEC 27001:2022

Se ha migrado de 114 a **93 controles**, simplificados en cuatro categorias:

1. **Organizacionales (37):** Gobernanza, politicas y gestion de activos.
2. **Personas (8):** Concienciación, términos de empleo y trabajo remoto.
3. **Fisicos (14):** Perimetros, entrada y seguridad de instalaciones.
4. **Tecnologicos (34):** Autenticacion, cifrado y gestion de vulnerabilidades.

---

## 3. Arquitectura Funcional de la Herramienta de Evaluacion

- **Definicion de Alcance (Clausula 4):** Captura limites fisicos, procesos y analisis estrategicos (DAFO/PESTEL).
- **Motor de Evaluacion (Rules Engine):** Cuestionarios dinamicos para cada norma.
- **Analisis de Brechas (GAP):** Compara estado actual vs 100% de cumplimiento.
- **Plan de Accion:** Repositorio de evidencias para cerrar GAPs.

---

## 4. Metodologia de Medicion y Escala de Madurez

- **0% = No Implementado:** Inexistencia absoluta del control.
- **25% = En Planificacion:** Existe evidencia de diseño o plan aprobado.
- **50% = Parcialmente Implementado:** Ejecucion inconsistente.
- **100% = Totalmente Implementado:** Cumplimiento cabal con evidencia.
- **N/A = No Aplica:** Requisito no relevante. Se excluye del denominador.

**Logica de Calculo:** Si un control es marcado como N/A, la herramienta recalcula el SoA automaticamente.

---

## 5. Especificaciones Tecnicas y Seguridad

- **Stack:** Python/FastAPI, PostgreSQL (prod), Chart.js
- **Gestion de Roles:**
  - **Administrador:** Control total del sistema.
  - **Auditor:** Creacion de evaluaciones, carga de hallazgos.
  - **JP Cliente:** Vision exclusiva de sus evaluaciones.
  - **Contraparte:** Consulta de avances y carga de evidencias.
- **Seguridad:** CSRF, XSS, JWT, Audit Trail inalterable.

---

## 6. Roadmap de Implementacion (12 pasos)

1. Analisis de Situacion Inicial
2. Mapa de Procesos
3. Politica y Planificacion
4. Procedimientos
5. Manual del Sistema
6. Capacitacion y Concienciacion
7. Implementacion Operativa
8. Auditoria Interna
9. Revision por la Direccion
10. Acciones Correctivas
11. Analisis para la Mejora Continua
12. Auditoria de Certificacion

---

## Estado Actual del Desarrollo

**Lo implementado (ISO 27001):**
- 93 controles ISO 27001:2022
- Escala de madurez 0-5 (CMMI)
- Evaluaciones por cliente
- Evidencias/documentos
- Dashboard con KPIs
- Graficos Chart.js
- Import/Export Excel
- Biblioteca de documentos
- Roles de usuario
- AuditLog completo

**Lo que falta por implementar:**
- Multi-norma (9001, 20000-1, 22301)
- Catalogo de Servicios + SLAs
- BIA (Business Impact Analysis)
- SoA automatizada
- N/A con justificacion
- Gestion de no conformidades
- Mapa de procesos
- DAFO/PESTEL

---

*Documento base para la planificacion del proyecto ISO 27001 Evaluator.*
