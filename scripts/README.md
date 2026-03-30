# Scripts de Gestión de Ollama

## 📋 Descripción

Estos scripts permiten iniciar y detener el servicio de Ollama de forma fácil y segura en Windows.

---

## 🚀 Uso Rápido

### Iniciar Ollama

**Opción 1 - PowerShell (Recomendado):**
```powershell
.\scripts\Start-Ollama.ps1
```

**Opción 2 - Batch:**
```cmd
.\scripts\start-ollama.bat
```

### Detener Ollama

**Opción 1 - PowerShell (Recomendado):**
```powershell
.\scripts\Stop-Ollama.ps1
```

**Opción 2 - Batch:**
```cmd
.\scripts\stop-ollama.bat
```

---

## 📁 Archivos Disponibles

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `Start-Ollama.ps1` | Script PowerShell para iniciar Ollama | `.\\Start-Ollama.ps1` |
| `stop-Ollama.ps1` | Script PowerShell para detener Ollama | `.\\Stop-Ollama.ps1` |
| `start-ollama.bat` | Script batch para iniciar Ollama | `start-ollama.bat` |
| `stop-ollama.bat` | Script batch para detener Ollama | `stop-ollama.bat` |

---

## 🔧 Características

### Start-Ollama.ps1
- ✅ Verifica si Ollama está instalado
- ✅ Comprueba si ya está corriendo
- ✅ Inicia Ollama en segundo plano
- ✅ Verifica que la conexión funcione
- ✅ Muestra modelos disponibles
- ✅ Mensajes claros y coloridos

### Stop-Ollama.ps1
- ✅ Verifica si Ollama está corriendo
- ✅ Detiene todos los procesos de Ollama
- ✅ Reintenta si es necesario
- ✅ Verifica que se detuvo correctamente
- ✅ Mensajes informativos

---

## 🎯 Ejemplos de Uso

### Flujo Normal - Iniciar Sesión

```powershell
# 1. Abrir PowerShell en la carpeta del proyecto
cd C:\Users\vpalma\Documents\Desarrollo\OpenCode_Antigravity\ISO27001_ITIL_seguridad

# 2. Iniciar Ollama
.\scripts\Start-Ollama.ps1

# 3. Verificar estado
ollama list

# 4. Trabajar normalmente
```

### Flujo Normal - Terminar Sesión

```powershell
# 1. Guardar todo el trabajo

# 2. Detener Ollama
.\scripts\Stop-Ollama.ps1

# 3. Verificar que se detuvo
Get-Process ollama -ErrorAction SilentlyContinue
# (No debería mostrar nada)
```

---

## 🔍 Solución de Problemas

### Error: "No se puede cargar el archivo"

**Causa:** PowerShell bloquea scripts no firmados

**Solución:**
```powershell
# Opción 1: Ejecutar con permiso temporal
powershell -ExecutionPolicy Bypass -File .\Start-Ollama.ps1

# Opción 2: Cambiar política permanentemente (admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "Ollama no encontrado"

**Causa:** Ollama no está en el PATH

**Solución:**
- Verifica que Ollama esté instalado: `ollama --version`
- Usa la ruta completa: `C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe`

### Error: "Puerto 11434 en uso"

**Causa:** Otro proceso usa el puerto

**Solución:**
```powershell
# Ver qué usa el puerto
netstat -ano | findstr 11434

# Matar el proceso
taskkill /F /PID <numero>
```

---

## 📊 Estados de Ollama

### Ollama NO está corriendo
```
[INFO] Ollama no está ejecutándose
[INFO] Iniciando Ollama...
[EXITO] Ollama se inició correctamente
```

### Ollama YA está corriendo
```
[INFO] Ollama ya está ejecutándose
PID: 12345
[EXITO] Ollama está listo para usar
```

### Ollama se detuvo correctamente
```
[INFO] Deteniendo Ollama...
[EXITO] Ollama se detuvo correctamente
Estado: DETENIDO
```

---

## 🎯 Mejores Prácticas

1. ✅ **Usa PowerShell** en lugar de batch (más características)
2. ✅ **Ejecuta como usuario normal** (no necesita admin)
3. ✅ **Espera 3 segundos** después de iniciar antes de usar
4. ✅ **Verifica el estado** con `ollama list`
5. ✅ **Detén Ollama** al terminar tu sesión
6. ✅ **No ejecutes múltiples instancias** de Ollama

---

## 📞 Comandos Relacionados

```powershell
# Verificar estado de Ollama
Get-Process ollama -ErrorAction SilentlyContinue

# Verificar conexión
Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing

# Ver modelos
ollama list

# Reiniciar Ollama
.\scripts\Stop-Ollama.ps1
.\scripts\Start-Ollama.ps1
```

---

## 📚 Documentación Adicional

- `docs/OLLAMA_START_STOP.md` - Guía completa de procedimientos
- `docs/QUICK_REFERENCE.md` - Referencia rápida de comandos
- `docs/AUDITOR_OFFLINE_GUIDE.md` - Guía para auditores
- `docs/AI_ON_DEMAND.md` - Documentación técnica de IA

---

**Versión:** 1.0  
**Actualizado:** 2026-03-30  
**Ollama:** v0.18.0  
**Plataforma:** Windows
