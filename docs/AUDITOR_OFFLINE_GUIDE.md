# Guía para Auditores - Modo Offline con IA Bajo Demanda

## 📋 Descripción

El sistema ISO 27001 Evaluator soporta **IA bajo demanda** con fallback automático, permitiendo trabajar en entornos con o sin conexión a internet.

## 🎯 Estados de IA

El sistema tiene 3 estados posibles:

### 🟢 Estado 1: IA Local Activa (Ollama)

**Indicador:** "🟢 IA Local Activa - llama3.2"

**Características:**
- ✅ 100% local - los datos no salen de tu equipo
- ✅ Privacidad total
- ✅ Ideal para auditorías in-situ
- ✅ Sin dependencia de internet

**Requisitos:**
- Ollama instalado y ejecutándose
- Comando: `ollama serve`

**Uso:**
1. Inicia Ollama: `ollama serve`
2. Abre la aplicación
3. El sistema detecta automáticamente Ollama
4. Usa las funciones de IA normalmente

---

### 🟡 Estado 2: IA Externa (NVIDIA NIM)

**Indicador:** "🟡 IA Externa (NVIDIA) - Llama 3.1 70B"

**Características:**
- ⚠️ Los datos se envían a NVIDIA
- ✅ Más rápido que Ollama local
- ✅ Modelos más potentes
- ⚠️ Requiere conexión a internet

**Requisitos:**
- API Key de NVIDIA configurada
- Conexión a internet

**Uso:**
1. Verifica tener `NVIDIA_API_KEY` en `.env`
2. El sistema usa NVIDIA automáticamente si Ollama no está disponible
3. Los datos se procesan en la nube de NVIDIA

---

### 🔴 Estado 3: Sin IA Disponible

**Indicador:** "🔴 Sin IA disponible - Evaluación manual"

**Características:**
- ❌ Sin funciones de IA
- ✅ Evaluación 100% manual
- ✅ Todo el trabajo se guarda
- ✅ Se puede recuperar con IA después

**Causas:**
- Ollama no está instalado
- Ollama no está ejecutándose
- NVIDIA API key no configurada
- Sin conexión a internet

**Qué hacer:**
1. **Opción A (Recomendada):** Iniciar Ollama
   ```bash
   ollama serve
   ```
2. **Opción B:** Continuar evaluación manual
   - Completa los controles manualmente
   - El sistema guarda todo
   - Re-analiza con IA cuando esté disponible

---

## 🔄 Flujo de Trabajo Offline

### Escenario 1: Auditoría en Sitio Sin Internet

**Preparación:**
1. Instala Ollama en tu laptop
2. Descarga el modelo: `ollama pull llama3.2`
3. Verifica que funciona: `ollama serve`

**Durante la auditoría:**
1. Inicia Ollama: `ollama serve`
2. Abre la aplicación
3. El sistema muestra: "🟢 IA Local Activa"
4. Trabaja normalmente con IA local

**Ventajas:**
- ✅ Sin necesidad de internet
- ✅ Privacidad total
- ✅ Respuesta rápida

---

### Escenario 2: Ollama Cae Durante Auditoría

**Síntomas:**
- El indicador cambia a "🔴 Sin IA"
- Las funciones de IA no responden
- Mensaje: "Ollama no está disponible"

**Qué hacer:**
1. **No entres en pánico** - tu trabajo manual está guardado
2. Reinicia Ollama:
   ```bash
   # Windows
   ollama serve
   
   # O verifica procesos
   taskkill /F /IM ollama.exe
   ollama serve
   ```
3. Recarga la página
4. El sistema detecta Ollama y muestra "🟢 IA Local"
5. **Botón "Recuperar con IA":** Re-analiza lo trabajado manualmente

---

### Escenario 3: Múltiples Auditores

**Situación:**
- Varios auditores trabajando en el mismo proyecto
- Cada uno con diferente estado de IA

**Comportamiento:**
- Cada auditor ve su propio estado de IA
- El trabajo se sincroniza automáticamente
- No hay conflictos de datos

**Recomendación:**
- Usar IA local si hay datos sensibles
- Coordinar quién usa IA para evitar duplicación

---

## 🛠️ Comandos Útiles

### Ollama

```bash
# Iniciar Ollama
ollama serve

# Verificar estado
ollama list

# Ver modelos instalados
ollama list

# Descargar modelo
ollama pull llama3.2

# Ver logs
ollama --debug

# Detener Ollama
taskkill /F /IM ollama.exe
```

### Verificación de Estado

```bash
# Verificar si Ollama responde
curl http://localhost:11434/api/tags

# Ver modelos disponibles
curl http://localhost:11434/api/tags
```

---

## 📊 Indicadores Visuales

### Sidebar (Siempre Visible)

```
┌─────────────────────────┐
│ 🟢 IA: Local            │
│    (llama3.2)           │
└─────────────────────────┘
```

- **🟢 Verde:** IA Local disponible
- **🟡 Amarillo:** IA Externa (NVIDIA)
- **🔴 Rojo:** Sin IA disponible
- **⏳ Cargando:** Verificando disponibilidad

### Página de Evaluación

En cada página de evaluación verás:
```
Evaluación: Cliente X
──────────────────────────
🟢 IA Local Activa - llama3.2
──────────────────────────
```

---

## 🔍 Solución de Problemas

### Problema: "Ollama no está disponible"

**Causas posibles:**
1. Ollama no está instalado
2. Ollama no está ejecutándose
3. Puerto 11434 bloqueado
4. Firewall bloquea la conexión

**Solución:**
```bash
# 1. Verificar instalación
ollama --version

# 2. Iniciar Ollama
ollama serve

# 3. Verificar puerto
netstat -an | grep 11434

# 4. Probar conexión
curl http://localhost:11434/api/tags
```

---

### Problema: "NVIDIA API key not configured"

**Causa:** No tienes API key de NVIDIA configurada

**Solución:**
1. Obtén API key en https://build.nvidia.com/
2. Agrega a tu `.env`:
   ```
   NVIDIA_API_KEY=tu_api_key_aqui
   ```
3. Reinicia la aplicación

---

### Problema: "Trabajo perdido al cambiar de IA"

**Síntomas:**
- Cambias de Ollama a NVIDIA
- El trabajo anterior no aparece

**Solución:**
- El sistema **NO** pierde trabajo
- Revisa que estés en la evaluación correcta
- Verifica el historial de cambios
- El trabajo manual siempre se preserva

---

## 📝 Mejores Prácticas

### Antes de la Auditoría

1. ✅ Verificar Ollama instalado
2. ✅ Probar modelo: `ollama run llama3.2 "hola"`
3. ✅ Verificar conexión: `curl http://localhost:11434/api/tags`
4. ✅ Tener backup de NVIDIA API key (si aplica)

### Durante la Auditoría

1. ✅ Iniciar Ollama antes de abrir la app
2. ✅ Verificar indicador "🟢 IA Local"
3. ✅ Guardar frecuentemente
4. ✅ Monitorear estado de IA

### Después de la Auditoría

1. ✅ Verificar que todo se guardó
2. ✅ Revisar historial de cambios
3. ✅ Documentar incidencias de IA
4. ✅ Cerrar Ollama si no se usa

---

## 🎯 Preguntas Frecuentes

### ¿Puedo trabajar sin internet?
**Sí**, con Ollama local puedes trabajar 100% offline.

### ¿Qué pasa si Ollama se cierra?
Tu trabajo manual se guarda. Reinicia Ollama y re-analiza.

### ¿Puedo cambiar entre Ollama y NVIDIA?
**Sí**, el sistema hace fallback automático.

### ¿El trabajo offline se sincroniza?
**Sí**, todo se guarda en la base de datos y sincroniza cuando hay conexión.

### ¿Cuánto tarda en detectar Ollama?
El sistema verifica cada 5 segundos automáticamente.

---

## 📞 Soporte

Para más información:
- Ver documentación en `docs/AI_STRATEGY.md`
- Revisar `docs/PROJECT_STATUS.md`
- Contactar al administrador del sistema

---

**Última actualización:** 2026-03-27  
**Versión:** v1.7.3
