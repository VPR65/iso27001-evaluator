@echo off
REM Forzar el modelo correcto antes de abrir opencode
set OPENCODE_MODEL=nvidia/qwen/qwen3-coder-480b-a35b-instruct
set OPENCODE_PROVIDER=nvidia

REM Abrir opencode GUI
start "" "opencode"

echo Modelo configurado: %OPENCODE_MODEL%
echo Abriendo GUI de opencode...
