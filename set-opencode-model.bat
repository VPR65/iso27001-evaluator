@echo off
echo Configurando modelo de opencode GUI...
echo.

REM 1. Cerrar cualquier instancia de opencode
taskkill /F /IM "opencode*.exe" 2>nul
taskkill /F /IM "electron*.exe" 2>nul

REM 2. Establecer variables de ambiente
setx OPENCODE_MODEL "nvidia/qwen/qwen3-coder-480b-a35b-instruct"
setx OPENCODE_PROVIDER "nvidia"

REM 3. Esperar a que se cierren los procesos
timeout /t 2 /nobreak >nul

REM 4. Abrir opencode GUI
start "" "opencode"

echo.
echo Modelo configurado: nvidia/qwen/qwen3-coder-480b-a35b-instruct
echo Por favor, verifica en la GUI que el modelo sea el correcto.
echo Si no es asi, busca en la GUI la opcion de Settings/Configuracion y cambia el modelo manualmente.
pause
