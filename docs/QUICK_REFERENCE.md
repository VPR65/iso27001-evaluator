# 🚀 Guía Rápida - Comandos Ollama

## ⚡ Comandos Esenciales (Windows)

### Iniciar Ollama
```powershell
# Opción 1: Script del proyecto
.\scripts\Start-Ollama.ps1

# Opción 2: Batch file
.\scripts\start-ollama.bat

# Opción 3: Manual
Start-Process 'C:\Users\vpalma\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve' -WindowStyle Hidden
```

### Detener Ollama
```powershell
# Opción 1: Script del proyecto
.\scripts\Stop-Ollama.ps1

# Opción 2: Batch file
.\scripts\stop-ollama.bat

# Opción 3: Manual
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Verificar Estado
```powershell
# Verificar proceso
Get-Process ollama -ErrorAction SilentlyContinue

# Verificar conexión
Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing

# Ver modelos
ollama list
```

---

## 📋 Flujo de Trabajo Diario

### Al Iniciar Sesión:
```powershell
# 1. Verificar si Ollama está corriendo
Get-Process ollama -ErrorAction SilentlyContinue

# 2. Si no está, iniciarlo
.\scripts\Start-Ollama.ps1

# 3. Verificar que funcione
Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing
```

### Al Terminar Sesión:
```powershell
# 1. Detener Ollama
.\scripts\Stop-Ollama.ps1

# 2. Verificar que se detuvo
Get-Process ollama -ErrorAction SilentlyContinue
```

---

## 🎯 Indicadores Visuales

| Icono | Estado | Acción |
|-------|--------|--------|
| 🟢 | IA Local Activa | ✅ Todo OK - Trabaja normalmente |
| 🟡 | IA Externa (NVIDIA) | ⚠️ Usando fallback - Datos externos |
| 🔴 | Sin IA | ❌ Inicia Ollama o trabaja manual |

---

## 🔧 Solución de Problemas Comunes

### Problema: "No se encuentra ollama"
```powershell
# Verificar instalación
ollama --version

# Si no existe, instalar
winget install Ollama
```

### Problema: "Puerto 11434 en uso"
```powershell
# Ver qué usa el puerto
netstat -ano | findstr 11434

# Matar el proceso
taskkill /F /PID <numero>
```

### Problema: "Ollama no responde"
```powershell
# Reiniciar Ollama
.\scripts\Stop-Ollama.ps1
.\scripts\Start-Ollama.ps1
```

---

## 📊 Modelos Disponibles

| Modelo | Tamaño | Uso Recomendado |
|--------|--------|-----------------|
| qwen3.5:0.8b | 873MB | Rápido, bajo consumo |
| phi3:mini | 3.8B | Balance velocidad/calidad |
| phi:latest | 3B | Tareas generales |
| llama3.1:latest | 8.0B | **Default** - Mejor balance |
| qwen2:7b | 7.6B | Alta calidad |

---

## 🎯 Comandos Rápidos (Cheat Sheet)

```powershell
# Inicio rápido
Get-Process ollama -ErrorAction SilentlyContinue || .\scripts\Start-Ollama.ps1

# Parada rápida
Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

# Verificación rápida
Get-Process ollama -ErrorAction SilentlyContinue; ollama list

# Estado completo
try {
    $r = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing
    $models = ($r.Content | ConvertFrom-Json).models
    Write-Host "Modelos: $($models.Count)"
    $models | ForEach-Object { Write-Host "  - $($_.name)" }
} catch {
    Write-Host "Ollama no disponible"
}
```

---

## 📞 Soporte

- **Documentación completa:** `docs/OLLAMA_START_STOP.md`
- **Guía auditores:** `docs/AUDITOR_OFFLINE_GUIDE.md`
- **Configuración IA:** `docs/AI_ON_DEMAND.md`

---

**Versión:** 1.0  
**Actualizado:** 2026-03-30  
**Ollama:** v0.18.0
