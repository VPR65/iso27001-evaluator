@echo off
REM =============================================================================
REM Script: stop-ollama.bat
REM Descripción: Detiene el servicio Ollama (Windows)
REM Uso: stop-ollama.bat o ejecutar directamente
REM =============================================================================

echo.
echo ===============================================
echo   DETENIENDO OLLAMA
echo ===============================================
echo.

REM Verificar si Ollama está corriendo
tasklist | findstr /i "ollama" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Ollama no está ejecutándose
    echo.
) else (
    echo [INFO] Deteniendo Ollama...
    echo.
    
    REM Detener Ollama forzosamente
    taskkill /F /IM ollama.exe >nul 2>nul
    
    REM Esperar 2 segundos
    timeout /t 2 /nobreak >nul
    
    REM Verificar que se detuvo
    tasklist | findstr /i "ollama" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [EXITO] Ollama se detuvo correctamente
        echo.
        echo Estado: DETENIDO
        echo.
    ) else (
        echo [ADVERTENCIA] Ollama podría no haberse detenido completamente
        echo.
        echo Intenta nuevamente o reinicia el equipo
        echo.
        
        REM Intentar una segunda vez
        echo [INFO] Intentando detener nuevamente...
        taskkill /F /IM ollama.exe >nul 2>nul
        timeout /t 2 /nobreak >nul
        
        tasklist | findstr /i "ollama" >nul 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo [EXITO] Ollama se detuvo en el segundo intento
        ) else (
            echo [ERROR] No se pudo detener Ollama
            echo.
            echo Cierra cualquier terminal que esté usando Ollama
            echo e intenta nuevamente
        )
    )
)

echo.
echo ===============================================
echo   Proceso completado
echo ===============================================
echo.

pause
