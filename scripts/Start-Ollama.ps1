# =============================================================================
# Script: Start-Ollama.ps1
# Descripción: Inicia el servicio Ollama en segundo plano (PowerShell)
# Uso: .\Start-Ollama.ps1 o .\Start-Ollama
# =============================================================================

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  INICIANDO OLLAMA - IA Local" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Ollama está instalado
try {
    $ollamaPath = Get-Command ollama -ErrorAction Stop
} catch {
    Write-Host "[ERROR] Ollama no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instala Ollama desde:" -ForegroundColor Yellow
    Write-Host "https://ollama.com/download" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Verificar si Ollama ya está corriendo
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue

if ($ollamaProcess) {
    Write-Host "[INFO] Ollama ya está ejecutándose" -ForegroundColor Green
    Write-Host ""
    Write-Host "PID: $($ollamaProcess.Id)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para verificar el estado:" -ForegroundColor Yellow
    Write-Host "  ollama list" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para detener Ollama:" -ForegroundColor Yellow
    Write-Host "  .\Stop-Ollama.ps1" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[INFO] Iniciando Ollama..." -ForegroundColor Yellow
    
    # Obtener ruta de Ollama
    $ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
    
    if (Test-Path $ollamaExe) {
        # Iniciar Ollama en segundo plano
        Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
        
        # Esperar 3 segundos
        Start-Sleep -Seconds 3
        
        # Verificar que inició
        $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
        
        if ($ollamaProcess) {
            Write-Host "[EXITO] Ollama se inició correctamente" -ForegroundColor Green
            Write-Host ""
            Write-Host "PID: $($ollamaProcess.Id)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Verificando conexión..." -ForegroundColor Yellow
            
            # Verificar conexión
            try {
                $response = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 5
                $models = ($response.Content | ConvertFrom-Json).models
                Write-Host "OK - Ollama responde correctamente" -ForegroundColor Green
                Write-Host "Modelos disponibles: $($models.Count)" -ForegroundColor Green
            } catch {
                Write-Host "ADVERTENCIA - Ollama responde pero hubo un error en la verificación" -ForegroundColor Yellow
            }
            
            Write-Host ""
            Write-Host "===============================================" -ForegroundColor Cyan
            Write-Host "  Ollama está listo para usar" -ForegroundColor Cyan
            Write-Host "===============================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Para ver modelos disponibles:" -ForegroundColor Yellow
            Write-Host "  ollama list" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Para detener Ollama:" -ForegroundColor Yellow
            Write-Host "  .\Stop-Ollama.ps1" -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host "[ERROR] No se pudo iniciar Ollama" -ForegroundColor Red
            Write-Host ""
            Write-Host "Verifica:" -ForegroundColor Yellow
            Write-Host "  1. Que Ollama esté instalado correctamente" -ForegroundColor Gray
            Write-Host "  2. Que el puerto 11434 no esté en uso" -ForegroundColor Gray
            Write-Host "  3. Los logs de Ollama para más detalles" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host "[ERROR] No se encontró Ollama en: $ollamaExe" -ForegroundColor Red
        Write-Host ""
        Write-Host "Verifica la instalación de Ollama" -ForegroundColor Yellow
        Write-Host ""
    }
}

Write-Host ""
