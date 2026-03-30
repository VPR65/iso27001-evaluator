# Sistema de IA On-Demand con Fallback Automático

## 📋 Descripción

El sistema ISO 27001 Evaluator implementa un **esquema de IA bajo demanda** con fallback automático en cascada, permitiendo trabajar en diversos entornos (con/sin internet, con/sin IA local).

## 🎯 Arquitectura de Fallback

El sistema sigue esta jerarquía de disponibilidad:

```
1. 🟢 Ollama Local (Preferido)
   ↓ (si no disponible)
2. 🟡 NVIDIA NIM (Fallback)
   ↓ (si no disponible)
3. 🔴 Sin IA (Evaluación manual)
```

## 🔍 Estados del Sistema

### Estado 🟢: IA Local (Ollama)

**Condiciones:**
- Ollama v0.18.0+ instalado y ejecutándose en `localhost:11434`
- Modelo configurado: `llama3.1:latest` (por defecto)
- Modelos disponibles: qwen3.5:0.8b, phi3:mini, phi:latest, llama3.1:latest, qwen2:7b

**Indicadores:**
- Icono: 🟢
- Mensaje: "IA Local Activa"
- Privacidad: "100% local - Datos no salen"
- Modelo: llama3.1:latest (8.0B Q4_K_M)

**Ventajas:**
- ✅ Privacidad total
- ✅ Sin dependencia de internet
- ✅ Ideal para auditorías in-situ
- ✅ Cumplimiento ISO 27001 estricto
- ✅ 5 modelos listos para usar

---

### Estado 🟡: IA Externa (NVIDIA NIM)

**Condiciones:**
- `NVIDIA_API_KEY` configurada
- Conexión a internet disponible
- Ollama NO disponible

**Indicadores:**
- Icono: 🟡
- Mensaje: "IA Externa (NVIDIA)"
- Privacidad: "⚠️ Datos se envían a NVIDIA"

**Consideraciones:**
- Los datos de evaluación se envían a API externa
- Requiere configuración previa de API key
- Más rápido que Ollama local (generalmente)

---

### Estado 🔴: Sin IA Disponible

**Condiciones:**
- Ollama NO disponible
- NVIDIA API key NO configurada O sin internet

**Indicadores:**
- Icono: 🔴
- Mensaje: "Sin IA disponible"
- Instrucciones: "Inicia Ollama con: ollama serve"

**Comportamiento:**
- El sistema permite evaluación 100% manual
- Todo el trabajo se guarda en la base de datos
- Al recuperar IA, ofrece re-analizar lo manual

---

## 🛠️ Implementación Técnica

### Backend (Python/FastAPI)

**`app/ai_service.py`:**
```python
class AIService:
    async def check_ollama_availability() -> Dict
    async def check_nvidia_availability() -> Dict
    async def get_ai_status() -> Dict
```

**Endpoints:**
- `GET /api/ai/status/detailed` - Retorna estado actual con fallback

### Frontend (JavaScript)

**`app/static/js/ai_status.js`:**
- Polling cada 5 segundos
- Detección automática de cambios
- Actualización de UI en tiempo real
- Eventos: `ai-status-changed`

### CSS

**`app/static/css/ai_status.css`:**
- Estilos para cada estado
- Animaciones de transición
- Responsive design

---

## 📊 Flujo de Trabajo

### Escenario 1: Auditoría con IA Local

```
1. Usuario inicia Ollama: ollama serve
2. Sistema detecta Ollama (🟢)
3. Usuario evalúa controles con IA local
4. Todo se guarda localmente
```

### Escenario 2: Caída de Ollama

```
1. Ollama se cierra inesperadamente
2. Sistema detecta caída (cambia a 🔴)
3. Usuario continúa evaluación manual
4. Sistema guarda trabajo manual
5. Usuario reinicia Ollama
6. Sistema detecta recuperación (🟢)
7. Ofrece re-analizar trabajo manual con IA
```

### Escenario 3: Sin Ollama, con NVIDIA

```
1. Ollama no disponible
2. Sistema verifica NVIDIA API key
3. Si existe: cambia a NVIDIA (🟡)
4. Si no: muestra 🔴 Sin IA
```

---

## 🔧 Configuración

### Variables de Ambiente

```bash
# Modo de IA
AI_MODE=ollama  # o 'nvidia'

# Configuración Ollama (Actualizado)
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.1:latest

# Modelos disponibles en tu entorno:
# - qwen3.5:0.8b (873MB Q8_0)
# - phi3:mini (3.8B Q4_0)
# - phi:latest (3B Q4_0)
# - llama3.1:latest (8.0B Q4_K_M) ← Default
# - qwen2:7b (7.6B Q4_0)

# Configuración NVIDIA (opcional - fallback)
NVIDIA_API_KEY=tu_api_key_aqui
AI_MODEL=meta/llama-3.1-70b-instruct
```

### Comandos Útiles (Windows)

```bash
# Verificar instalación
ollama --version
# Tu versión: 0.18.0

# Iniciar Ollama (PowerShell)
Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden

# Iniciar Ollama (CMD)
start "" "C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe" serve

# Verificar estado
ollama list

# Probar conexión (PowerShell)
Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing

# Ver modelos
ollama list

# Descargar modelo adicional
ollama pull llama3.1

# Detener Ollama (PowerShell)
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# Detener Ollama (CMD)
taskkill /F /IM ollama.exe
```

---

## 📈 Métricas de Rendimiento

### Tiempos de Respuesta (promedio)

| Proveedor | Tiempo Respuesta | Privacidad | Modelos Disponibles |
|-----------|-----------------|------------|---------------------|
| Ollama Local | 2-10 segundos | 100% local | qwen3.5:0.8b, phi3:mini, phi:latest, llama3.1:latest, qwen2:7b |
| NVIDIA NIM | 1-3 segundos | ⚠️ Externo | Llama 3.1 70B, Mistral Large, etc. |
| Sin IA | N/A (manual) | 100% local | - |

### Frecuencia de Monitoreo

- **Polling:** Cada 5 segundos
- **Cache:** 5 segundos (evita llamadas excesivas)
- **Impacto:** Mínimo (< 1% CPU)
- **Tu entorno:** Ollama v0.18.0 en localhost:11434

---

## 🔍 Solución de Problemas

### Problema: "Ollama no disponible" constantemente

**Causas:**
1. Ollama no está instalado (tu versión: 0.18.0)
2. Ollama no está ejecutándose en segundo plano
3. Puerto 11434 bloqueado por firewall

**Solución:**
```powershell
# Verificar instalación
ollama --version
# Debería mostrar: ollama version is 0.18.0

# Iniciar Ollama (PowerShell - recomendado)
Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden

# Iniciar Ollama (CMD)
start "" "C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe" serve

# Verificar puerto
netstat -an | findstr 11434

# Verificar proceso
Get-Process ollama -ErrorAction SilentlyContinue
```

---

### Problema: Fallback a NVIDIA no funciona

**Causas:**
1. API key no configurada
2. Sin conexión a internet
3. API key inválida

**Solución:**
1. Verificar `.env` tiene `NVIDIA_API_KEY`
2. Probar conexión: `curl https://integrate.api.nvidia.com`
3. Verificar logs de la aplicación

---

## 📚 Documentación Relacionada

- `AUDITOR_OFFLINE_GUIDE.md` - Guía para auditores
- `AI_STRATEGY.md` - Estrategia de IA
- `PROJECT_STATUS.md` - Estado del proyecto
- `CHANGELOG.md` - Historial de cambios

---

## 🎯 Mejores Prácticas

### Para Auditores

1. ✅ Iniciar Ollama antes de auditoría: `ollama serve` o PowerShell
2. ✅ Verificar indicador 🟢 antes de empezar
3. ✅ Verificar modelos: `ollama list` (tienes 5 modelos)
4. ✅ Tener backup de NVIDIA API key (fallback)
5. ✅ Documentar incidencias de IA
6. ✅ Usar modelo predeterminado: llama3.1:latest

### Para Administradores

1. ✅ Monitorear logs de Ollama (v0.18.0)
2. ✅ Actualizar modelos periódicamente: `ollama pull <modelo>`
3. ✅ Verificar espacio en disco (~15GB para tus 5 modelos)
4. ✅ Backup de configuración de IA (.env)
5. ✅ Mantener Ollama actualizado (actual: 0.18.0)
6. ✅ Configurar inicio automático en Windows

---

**Última actualización:** 2026-03-27  
**Versión:** v1.7.4  
**Estado:** En Producción
