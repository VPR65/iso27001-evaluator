# PLAN DE PRUEBAS - ISO 27001 Evaluator

> Version: 1.1.0 | Ultima actualizacion: 2026-03-22

---

## 1. TIPOS DE PRUEBA

| Tipo             | Objetivo                                          | Herramienta           |
|------------------|--------------------------------------------------|-----------------------|
| Unitaria         | Verificar funciones individuales                   | pytest (futuro)       |
| Integracion      | Verificar que los modulos funcionan juntos        | FastAPI TestClient    |
| Funcional        | Verificar que las funcionalidades usan correctamente| Navegador manual      |
| Aceptacion       | Validar con el usuario final                      | Revisiones del usuario|
| Seguridad        | Verificar que no hay vulnerabilidades conocidas    | Revision de codigo    |

---

## 2. PRUEBAS FUNCIONALES (QA)

### 2.1 Modulo: Autenticacion

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| AU-1 | Login con credenciales correctas        | Redirige a /dashboard     | PEND   |
| AU-2 | Login con password incorrecto           | Mensaje de error visible  | PEND   |
| AU-3 | Login con email no registrado           | Mensaje de error visible  | PEND   |
| AU-4 | Logout limpia sesion                   | Cookie eliminado, redirige a login | PEND |
| AU-5 | Sesion expirada redirige a login       | Redirige automaticamente   | PEND   |
| AU-6 | Acceder a /dashboard sin sesion        | Redirige a /login        | PEND   |

### 2.2 Modulo: Dashboard

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| DA-1 | Dashboard muestra KPIs                 | Cards con numeros visibles | PEND   |
| DA-2 | Dashboard muestra score de madurez      | Numero 0-5 con color      | PEND   |
| DA-3 | Dashboard muestra evaluaciones recientes| Lista con max 5 items     | PEND   |
| DA-4 | Boton "Nueva Evaluacion" funciona      | Navega a /evaluations/new  | PEND   |
| DA-5 | Reloj muestra hora actual              | Actualizacion en tiempo real | PEND |
| DA-6 | Sidebar se colapsa al hacer clic       | Ancho cambia a 68px        | PEND   |

### 2.3 Modulo: Evaluaciones

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| EV-1 | Crear nueva evaluacion                 | Redirige a detalle        | PEND   |
| EV-2 | Listado muestra todas las evaluaciones  | Tabla con evaluaciones     | PEND   |
| EV-3 | Ver detalle de evaluacion              | Muestra dominios colapsados| PEND  |
| EV-4 | Iniciar evaluacion                    | Status cambia a IN_PROGRESS | PEND  |
| EV-5 | Evaluar un control (nivel 3)          | Se guarda madurez = 3      | PEND   |
| EV-6 | Evaluar con evidencia (archivo)        | Archivo se sube y guarda  | PEND   |
| EV-7 | Completar evaluacion                  | Status cambia a COMPLETED  | PEND   |
| EV-8 | Eliminar evaluacion                   | Desaparece del listado    | PEND   |

### 2.4 Modulo: Estadisticas

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| ST-1 | Stats sin evaluacion                   | Muestra 0 en todo        | PEND   |
| ST-2 | Stats con evaluacion completa           | Grafico de barras visible  | PEND   |
| ST-3 | Stats con evaluacion parcial           | Grafico con datos parciales | PEND  |
| ST-4 | Controles criticos marcados            | Fila roja si nivel < 2    | PEND   |
| ST-5 | Radar chart muestra dominios           | Grafico polar con 4 ejes   | PEND   |

### 2.5 Modulo: RFCs

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| RF-1 | Crear RFC con P2                       | Se crea y muestra en lista | PEND   |
| RF-2 | Cambiar estado a Approved              | Boton de workflow visible  | PEND   |
| RF-3 | Cambiar estado a Rejected              | Badge "rejected" visible   | PEND   |
| RF-4 | Prioridad calculada correctamente        | P1 + alto impacto = P1     | PEND   |

### 2.6 Modulo: Documentos

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| DO-1 | Crear documento tipo "Politica"        | Se guarda con v0.0.1       | PEND   |
| DO-2 | Crear nueva version                    | Version incrementa         | PEND   |
| DO-3 | Ver diff entre versiones               | Muestra diferencias         | PEND   |
| DO-4 | Rollback a version anterior            | Contenido vuelve al anterior | PEND  |
| DO-5 | Cambiar estado a Published              | Badge "published" visible   | PEND   |

### 2.7 Modulo: Sprints

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| SP-1 | Crear sprint activo                    | Se muestra en listado      | PEND   |
| SP-2 | Agregar item al backlog                | Item aparece en backlog    | PEND   |
| SP-3 | Agregar tarea a un item                | Tarea aparece en item      | PEND   |
| SP-4 | Completar tarea                         | % completado aumenta       | PEND   |

### 2.8 Modulo: Import/Export

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| IM-1 | Exportar evaluacion a Excel            | Archivo .xlsx se descarga  | PEND   |
| IM-2 | Importar Excel con datos validos       | Evaluacion se llena        | PEND   |
| IM-3 | Importar Excel con formato incorrecto   | Mensaje de error visible   | PEND   |

### 2.9 Modulo: Multi-tenant

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| MT-1 | Admin Demo no ve clientes de otros     | Solo ve "Cliente Demo"     | PEND   |
| MT-2 | Superadmin ve todos los clientes       | Lista completa visible      | PEND   |
| MT-3 | Evaluacion de Demo no accesible por otro| Error 403                  | PEND   |

---

## 3. PRUEBAS DE SEGURIDAD

| ID   | Caso de prueba                         | Resultado esperado         | Estado |
|------|----------------------------------------|---------------------------|--------|
| SE-1 | XSS en campo de evaluacion            | Codigo no se ejecuta       | PEND   |
| SE-2 | SQL injection en parametros URL        | No hay error de SQL        | PEND   |
| SE-3 | Acceder a /admin sin ser superadmin    | Error 403                 | PEND   |
| SE-4 | Subir archivo .exe como evidencia      | Archivo rechazado          | PEND   |
| SE-5 | Subir archivo > 10MB                   | Archivo rechazado          | PEND   |
| SE-6 | Password vacio en login                | Validacion del form        | PEND   |

---

## 4. EJECUTAR PRUEBAS

### 4.1 Pruebas Manuales (TestClient)

```bash
# Ejecutar todas las pruebas basicas
cd "C:/Users/vpalma/Documents/Desarrollo/OpenCode_Antigravity/ISO27001_ITIL_seguridad"
python -c "
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# AU-1: Login correcto
r = client.post('/login', data={'email': 'admin@iso27001.local', 'password': 'admin123'}, follow_redirects=False)
assert r.status_code == 302, f'AU-1 FALLO: {r.status_code}'

# AU-2: Login incorrecto
r = client.post('/login', data={'email': 'admin@iso27001.local', 'password': 'mal'}, follow_redirects=False)
assert r.status_code == 200, f'AU-2 FALLO'
assert 'error' in r.text.lower(), 'AU-2 FALLO: error no visible'

# DA-1: Dashboard carga
r = client.get('/dashboard')
assert r.status_code == 200, f'DA-1 FALLO: {r.status_code}'

print('AU-1: OK | AU-2: OK | DA-1: OK')
"
```

### 4.2 Pruebas de Endpoints con TestClient

```bash
# Ejecutar con autenticacion
python -c "
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
session = client.post('/login', data={
    'email': 'admin@iso27001.local',
    'password': 'admin123'
}, follow_redirects=False)

# Probar endpoints autenticados
for path in ['/dashboard', '/evaluations', '/rfcs', '/documents', '/sprints', '/clients']:
    r = client.get(path)
    print(f'{path}: {r.status_code}')
"
```

---

## 5. CRITERIOS DE ACEPTACION

| Criterio                          | Objetivo    | Actual |
|------------------------------------|-------------|--------|
| Pruebas funcionales pasadas         | 100%        | 0%    |
| Pruebas de seguridad pasadas         | 100%        | 0%    |
| Sin errores 500 en uso normal       | 0 errores   | -      |
| Tiempo de carga de pagina           | < 2 seg     | -      |
| Login funcional                    | 100%        | -      |

---

## 6. REPORTE DE BUGS

Para reportar un bug, incluir:

1. **ID del test**: (ej: EV-5)
2. **Pasos para reproducir**: Paso a paso
3. **Resultado esperado**: Que deberia pasar
4. **Resultado actual**: Que paso realmente
5. **Severidad**: Critica / Alta / Media / Baja
6. **Evidencia**: Screenshots, logs del navegador
