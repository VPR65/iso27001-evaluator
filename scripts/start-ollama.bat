@echo off
REM =============================================================================
# Script: start-ollama.bat
# Descripción: Inicia el servicio Ollama en segundo plano (Windows)
# Uso: start-ollama.bat o ejecutar directamente
# =============================================================================

echo.
echo ===============================================
echo   INICIANDO OLLAMA - IA Local
echo ===============================================
echo.

REM Verificar si Ollama está instalado
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama no está instalado o no está en el PATH
    echo.
    echo Por favor, instala Ollama desde:
    echo https://ollama.com/download
    echo.
    pause
    exit /b 1
)

REM Verificar si Ollama ya está corriendo
tasklist | findstr /i "ollama" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Ollama ya está ejecutándose
    echo.
    echo Para verificar el estado:
    echo   ollama list
    echo.
    echo Para detener Ollama:
    echo   stop-ollama.bat
    echo.
) else (
    echo [INFO] Iniciando Ollama...
    echo.
    
    REM Iniciar Ollama en segundo plano
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    
    REM Esperar 3 segundos
    timeout /t 3 /nobreak >nul
    
    REM Verificar que inició
    tasklist | findstr /i "ollama" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [EXITO] Ollama se inició correctamente
        echo.
        echo Verificando conexión...
        powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 5; Write-Host 'OK - Ollama responde correctamente' -ForegroundColor Green } catch { Write-Host 'ERROR - Ollama no responde' -ForegroundColor Red }"
        echo.
        echo ===============================================
        echo   Ollama está listo para usar
        echo ===============================================
        echo.
        echo Para ver modelos disponibles:
        echo   ollama list
        echo.
        echo Para detener Ollama:
        echo   stop-ollama.bat
        echo.
    ) else (
        echo [ERROR] No se pudo iniciar Ollama
        echo.
        echo Verifica:
        echo   1. Que Ollama esté instalado correctamente
        echo   2. Que el puerto 11434 no esté en uso
        echo   3. Los logs de Ollama para más detalles
        echo.
    )
)

echo.
pause
