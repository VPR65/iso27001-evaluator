# ISO 27001 Evaluator - Script de Despliegue Automático
# Uso: .\scripts\deploy.ps1
# Descripción: Despliega la aplicación con Docker Compose

param(
    [string]$Environment = "development",  # development, qa, production
    [switch]$WithOllama,                   # Incluir Ollama (IA local)
    [switch]$NoCache                       # Sin cache de Docker
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ISO 27001 Evaluator - Deploy Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Validar entorno
if ($Environment -notin @("development", "qa", "production")) {
    Write-Host "Error: Environment debe ser 'development', 'qa' o 'production'" -ForegroundColor Red
    exit 1
}

Write-Host "Entorno: $Environment" -ForegroundColor Yellow
Write-Host "Ollama: $(if ($WithOllama) { "Incluido" } else { "No incluido" })`n" -ForegroundColor Yellow

# Verificar Docker
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker instalado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Verificar archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "`n[WARN] No se encontró .env, copiando desde .env.docker..." -ForegroundColor Yellow
    if (Test-Path ".env.docker") {
        Copy-Item ".env.docker" ".env"
        Write-Host "[OK] .env creado. Edítalo con tus valores antes de continuar." -ForegroundColor Green
        Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
        Read-Host
    } else {
        Write-Host "[ERROR] No se encontró .env.docker" -ForegroundColor Red
        exit 1
    }
}

# Construir comando docker-compose
$composeCmd = "docker-compose"
if ($WithOllama) {
    $composeCmd += " --profile ollama"
}

# Construir opciones de build
$buildOpts = ""
if ($NoCache) {
    $buildOpts = "--no-cache"
}

Write-Host "`n[INFO] Iniciando despliegue..." -ForegroundColor Cyan

# Detener servicios existentes
Write-Host "`n[1/4] Deteniendo servicios existentes..." -ForegroundColor Yellow
docker-compose down

# Construir imágenes
Write-Host "`n[2/4] Construyendo imágenes..." -ForegroundColor Yellow
Invoke-Expression "$composeCmd build $buildOpts"

# Iniciar servicios
Write-Host "`n[3/4] Iniciando servicios..." -ForegroundColor Yellow
Invoke-Expression "$composeCmd up -d"

# Esperar a que los servicios estén listos
Write-Host "`n[4/4] Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar estado
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Estado de los Servicios" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

docker-compose ps

# Verificar health
Write-Host "`nVerificando salud de los servicios..." -ForegroundColor Yellow

# Verificar App
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Aplicación respondiendo en http://localhost:8000" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] La aplicación aún no responde (puede estar iniciando)" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Despliegue Completado" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Comandos útiles:" -ForegroundColor Yellow
Write-Host "  Ver logs:        docker-compose logs -f" -ForegroundColor Gray
Write-Host "  Detener:         docker-compose down" -ForegroundColor Gray
Write-Host "  Reiniciar:       docker-compose restart" -ForegroundColor Gray
Write-Host "  Estado:          docker-compose ps`n" -ForegroundColor Gray

if ($WithOllama) {
    Write-Host "IA Local (Ollama) está disponible en: http://localhost:11434" -ForegroundColor Cyan
}

Write-Host "Aplicación web: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Login: http://localhost:8000/login`n" -ForegroundColor Cyan
