# ISO 27001 Evaluator - Script de Instalación Automática
# Uso: .\scripts\install.ps1
# Descripción: Instala todas las dependencias y configura el entorno

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ISO 27001 - Instalación Automática" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$ErrorCount = 0

# ============================================
# 1. Verificar Python
# ============================================
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version
    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no está instalado" -ForegroundColor Red
    Write-Host "Descarga desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    $ErrorCount++
}

# ============================================
# 2. Verificar pip
# ============================================
Write-Host "`n[2/6] Verificando pip..." -ForegroundColor Yellow

try {
    $pipVersion = pip --version
    Write-Host "[OK] pip instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip no está instalado" -ForegroundColor Red
    $ErrorCount++
}

# ============================================
# 3. Instalar dependencias
# ============================================
Write-Host "`n[3/6] Instalando dependencias..." -ForegroundColor Yellow

try {
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt --upgrade
        Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "[WARN] requirements.txt no encontrado" -ForegroundColor Yellow
        $ErrorCount++
    }
} catch {
    Write-Host "[ERROR] Error instalando dependencias: $_" -ForegroundColor Red
    $ErrorCount++
}

# ============================================
# 4. Verificar/Ollama
# ============================================
Write-Host "`n[4/6] Verificando Ollama..." -ForegroundColor Yellow

try {
    $ollamaVersion = ollama --version
    Write-Host "[OK] Ollama: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Ollama no está instalado (opcional)" -ForegroundColor Yellow
    Write-Host "Para IA local, instala desde: https://ollama.com" -ForegroundColor Gray
}

# ============================================
# 5. Crear .env
# ============================================
Write-Host "`n[5/6] Configurando entorno..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] .env creado desde .env.example" -ForegroundColor Green
        Write-Host "[WARN] Edita .env con tus valores" -ForegroundColor Yellow
    } elseif (Test-Path ".env.docker") {
        Copy-Item ".env.docker" ".env"
        Write-Host "[OK] .env creado desde .env.docker" -ForegroundColor Green
        Write-Host "[WARN] Edita .env con tus valores" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] Creando .env básico..." -ForegroundColor Yellow
        @"
SECRET_KEY=cambio-esto-en-produccion
DATABASE_URL=sqlite:///./iso27001.db
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.1:latest
"@ | Out-File ".env" -Encoding UTF8
        Write-Host "[OK] .env básico creado" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] .env ya existe" -ForegroundColor Green
}

# ============================================
# 6. Inicializar BD
# ============================================
Write-Host "`n[6/6] Inicializando base de datos..." -ForegroundColor Yellow

try {
    # Intentar crear las tablas
    python -c "from app.database import create_db_and_tables; create_db_and_tables()"
    Write-Host "[OK] Base de datos inicializada" -ForegroundColor Green
} catch {
    Write-Host "[INFO] La BD se creará al iniciar la app" -ForegroundColor Yellow
}

# ============================================
# Resumen
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Instalación Completada" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($ErrorCount -eq 0) {
    Write-Host "[OK] Instalación exitosa" -ForegroundColor Green
    Write-Host "`nSiguientes pasos:" -ForegroundColor Yellow
    Write-Host "1. Editar .env con tus valores" -ForegroundColor Gray
    Write-Host "2. Iniciar la app: uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host "3. Abrir: http://localhost:8000" -ForegroundColor Gray
} else {
    Write-Host "[WARN] $ErrorCount errores encontrados" -ForegroundColor Yellow
    Write-Host "Revisa los mensajes anteriores" -ForegroundColor Yellow
}

Write-Host "`nPresiona Enter para continuar..." -ForegroundColor Yellow
Read-Host
