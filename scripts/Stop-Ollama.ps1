# =============================================================================
# Script: Stop-Ollama.ps1
# Descripción: Detiene el servicio Ollama (PowerShell)
# Uso: .\Stop-Ollama.ps1 o .\Stop-Ollama
# =============================================================================

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  DETENIENDO OLLAMA" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Ollama está corriendo
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue

if (-not $ollamaProcess) {
    Write-Host "[INFO] Ollama no está ejecutándose" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[INFO] Deteniendo Ollama..." -ForegroundColor Yellow
    Write-Host ""
    
    # Mostrar procesos de Ollama
    Write-Host "Procesos encontrados:" -ForegroundColor Gray
    $ollamaProcess | ForEach-Object {
        Write-Host "  PID: $($_.Id) - Nombre: $($_.ProcessName)" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Detener Ollama forzosamente
    try {
        $ollamaProcess | Stop-Process -Force
        
        # Esperar 2 segundos
        Start-Sleep -Seconds 2
        
        # Verificar que se detuvo
        $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
        
        if (-not $ollamaProcess) {
            Write-Host "[EXITO] Ollama se detuvo correctamente" -ForegroundColor Green
            Write-Host ""
            Write-Host "Estado: DETENIDO" -ForegroundColor Green
            Write-Host ""
        } else {
            Write-Host "[ADVERTENCIA] Ollama podría no haberse detenido completamente" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Intentando detener nuevamente..." -ForegroundColor Yellow
            Write-Host ""
            
            # Intentar una segunda vez
            $ollamaProcess | Stop-Process -Force
            Start-Sleep -Seconds 2
            
            $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
            
            if (-not $ollamaProcess) {
                Write-Host "[EXITO] Ollama se detuvo en el segundo intento" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] No se pudo detener Ollama" -ForegroundColor Red
                Write-Host ""
                Write-Host "Cierra cualquier terminal que esté usando Ollama" -ForegroundColor Yellow
                Write-Host "e intenta nuevamente, o reinicia el equipo" -ForegroundColor Yellow
                Write-Host ""
            }
        }
    } catch {
        Write-Host "[ERROR] Error al detener Ollama: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Intenta con CMD:" -ForegroundColor Yellow
        Write-Host "  taskkill /F /IM ollama.exe" -ForegroundColor Gray
        Write-Host ""
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Proceso completado" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
