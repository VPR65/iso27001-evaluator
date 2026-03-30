# Procedimiento para Iniciar y Detener Ollama

## 📋 Descripción

Este documento describe los procedimientos para **iniciar (subir)** y **detener (bajar)** el servicio de Ollama en diferentes sistemas operativos.

---

## 🔹 ¿Cuándo usar este procedimiento?

### Debes INICIAR Ollama cuando:
- ✅ El indicador muestre "🔴 Sin IA disponible"
- ✅ Vayas a realizar evaluaciones con IA local
- ✅ El sistema indique "Ollama no está disponible"
- ✅ Vayas a trabajar offline con IA

### Debes DETENER Ollama cuando:
- ✅ Hayas terminado tu sesión de trabajo
- ✅ Necesites liberar recursos del equipo
- ✅ Vayas a actualizar Ollama
- ✅ El sistema indique problemas de conexión

---

## 🖥️ WINDOWS (Tu entorno actual)

### Opción 1: Script Automático (Recomendado)

#### Iniciar Ollama:
```powershell
# Ejecuta este script: start-ollama.ps1
.\scripts\start-ollama.ps1
```

#### Detener Ollama:
```powershell
# Ejecuta este script: stop-ollama.ps1
.\scripts\stop-ollama.ps1
```

### Opción 2: Comandos Manuales

#### A. Iniciar Ollama (PowerShell)

```powershell
# Método 1: Como proceso en segundo plano
Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden

# Método 2: Usando Start-Process con ruta completa
Start-Process -FilePath "C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe" -ArgumentList "serve"

# Verificar que inició
Get-Process ollama -ErrorAction SilentlyContinue
```

#### B. Iniciar Ollama (CMD - Símbolo del sistema)

```cmd
REM Método 1: Usando start
start "" "C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe" serve

REM Verificar que inició
tasklist | findstr ollama
```

#### C. Detener Ollama (PowerShell)

```powershell
# Método 1: Forzar detención
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# Método 2: Detener suavemente
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process

# Verificar que se detuvo
Get-Process ollama -ErrorAction SilentlyContinue
# (No debería mostrar nada)
```

#### D. Detener Ollama (CMD)

```cmd
REM Método 1: Usando taskkill
taskkill /F /IM ollama.exe

REM Verificar que se detuvo
tasklist | findstr ollama
REM (No debería mostrar nada)
```

### Opción 3: Scripts de Acceso Directo

Se proporcionan dos scripts en la carpeta `scripts/`:

1. **start-ollama.bat** - Inicia Ollama
2. **stop-ollama.bat** - Detiene Ollama

---

## 🐧 LINUX / MAC

### Iniciar Ollama

```bash
# Método 1: Como servicio (si está configurado)
sudo systemctl start ollama

# Método 2: Manual en segundo plano
ollama serve &

# Método 3: Con systemd
sudo systemctl start ollama
sudo systemctl enable ollama
```

### Detener Ollama

```bash
# Método 1: Como servicio
sudo systemctl stop ollama

# Método 2: Matar proceso
pkill ollama

# Método 3: Usando kill
killall ollama
```

### Verificar estado

```bash
# Verificar proceso
ps aux | grep ollama

# Verificar puerto
netstat -tlnp | grep 11434

# Verificar conexión
curl http://localhost:11434/api/tags
```

---

## 📱 VERIFICACIÓN RÁPIDA

### Verificar si Ollama está corriendo

#### Windows (PowerShell):
```powershell
Get-Process ollama -ErrorAction SilentlyContinue
```

#### Windows (CMD):
```cmd
tasklist | findstr ollama
```

#### Linux/Mac:
```bash
ps aux | grep ollama
```

### Verificar si Ollama responde

#### Windows (PowerShell):
```powershell
try {
    $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 2
    Write-Host "✅ Ollama está responding" -ForegroundColor Green
    $response.Content
} catch {
    Write-Host "❌ Ollama no responde" -ForegroundColor Red
}
```

#### Linux/Mac:
```bash
curl -s http://localhost:11434/api/tags
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema 1: "No se puede encontrar ollama"

**Causa:** Ollama no está en el PATH del sistema

**Solución:**
```powershell
# Windows - Usar ruta completa
Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve'
```

### Problema 2: "El puerto 11434 está en uso"

**Causa:** Otro proceso usa el puerto

**Solución:**
```powershell
# Windows - Ver qué usa el puerto
netstat -ano | findstr 11434

# Matar el proceso
taskkill /F /PID <PID>
```

### Problema 3: Ollama no inicia

**Causa:** Instalación corrupta

**Solución:**
```powershell
# Windows - Reinstalar
winget uninstall Ollama
winget install Ollama
```

---

## 📊 FLUJO RECOMENDADO

### Al iniciar sesión:
```
1. Verificar si Ollama está corriendo
   Get-Process ollama -ErrorAction SilentlyContinue

2. Si NO está corriendo → Iniciar
   .\scripts\start-ollama.ps1

3. Verificar que responde
   Invoke-WebRequest -Uri 'http://localhost:11434/api/tags'

4. Ver indicador en la aplicación
   Debe mostrar: 🟢 IA Local Activa
```

### Al terminar sesión:
```
1. Guardar todo el trabajo

2. Detener Ollama
   .\scripts\stop-ollama.ps1

3. Verificar que se detuvo
   Get-Process ollama -ErrorAction SilentlyContinue
   (No debería mostrar nada)
```

---

## 🎯 MEJORES PRÁCTICAS

1. ✅ **Inicia Ollama al comenzar** tu sesión de trabajo
2. ✅ **Verifica el indicador** 🟢 antes de trabajar
3. ✅ **Detén Ollama al finalizar** para liberar recursos
4. ✅ **No cierres la terminal** si iniciaste Ollama manualmente
5. ✅ **Usa los scripts** para evitar errores
6. ✅ **Verifica regularmente** que Ollama responde

---

## 📞 COMANDOS RÁPIDOS (Cheat Sheet)

```powershell
# INICIAR (PowerShell)
Get-Process ollama -ErrorAction SilentlyContinue || Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden

# DETENER (PowerShell)
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# VERIFICAR (PowerShell)
Get-Process ollama -ErrorAction SilentlyContinue; Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing | Select-Object -ExpandProperty Content

# VER MODELOS
ollama list
```

---

**Última actualización:** 2026-03-30  
**Versión:** 1.0  
**Ollama:** v0.18.0  
**Modelos:** qwen3.5:0.8b, phi3:mini, phi:latest, llama3.1:latest, qwen2:7b
