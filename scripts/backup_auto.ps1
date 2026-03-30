# ISO 27001 Evaluator - Backup Automático
# Uso: .\scripts\backup_auto.ps1 [-RetentionDays 7] [-BackupDir "backups"]
# Descripción: Realiza backup automático de BD, uploads y configuración

param(
    [int]$RetentionDays = 7,      # Días de retención de backups
    [string]$BackupDir = "backups", # Directorio de backups
    [switch]$Auto                  # Modo automático (sin prompts)
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "backup_auto_$timestamp"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ISO 27001 - Backup Automático" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "Timestamp: $timestamp" -ForegroundColor Yellow
Write-Host "Retención: $RetentionDays días`n" -ForegroundColor Yellow

# Crear directorio de backups si no existe
if (-not (Test-Path $BackupDir)) {
    Write-Host "[INFO] Creando directorio de backups..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

$backupPath = Join-Path $BackupDir $backupName
New-Item -ItemType Directory -Path $backupPath | Out-Null

Write-Host "[OK] Directorio creado: $backupPath`n" -ForegroundColor Green

# ============================================
# 1. Backup de Base de Datos
# ============================================
Write-Host "[1/3] Backup de Base de Datos..." -ForegroundColor Yellow

try {
    # Verificar si hay contenedores Docker
    $dbContainer = docker-compose ps -q db 2>$null
    
    if ($dbContainer) {
        # Backup desde Docker
        $dbBackupFile = Join-Path $backupPath "database.sql"
        docker-compose exec -T db pg_dump -U iso27001 iso27001 > $dbBackupFile
        Write-Host "[OK] Database backup: database.sql" -ForegroundColor Green
    } else {
        # Backup desde SQLite (si existe)
        $sqliteDb = "iso27001.db"
        if (Test-Path $sqliteDb) {
            Copy-Item $sqliteDb (Join-Path $backupPath "iso27001.db")
            Write-Host "[OK] SQLite backup: iso27001.db" -ForegroundColor Green
        } else {
            Write-Host "[WARN] No se encontró base de datos" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[ERROR] Error en backup de BD: $_" -ForegroundColor Red
}

# ============================================
# 2. Backup de Uploads
# ============================================
Write-Host "`n[2/3] Backup de Uploads..." -ForegroundColor Yellow

try {
    $uploadsDir = "uploads"
    if (Test-Path $uploadsDir) {
        $uploadsBackup = Join-Path $backupPath "uploads"
        Copy-Item -Path $uploadsDir -Destination $uploadsBackup -Recurse -Force
        Write-Host "[OK] Uploads backup completado" -ForegroundColor Green
        
        # Contar archivos
        $fileCount = (Get-ChildItem -Path $uploadsBackup -Recurse -File).Count
        Write-Host "     Archivos: $fileCount" -ForegroundColor Gray
    } else {
        Write-Host "[INFO] No hay directorio de uploads" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Error en backup de uploads: $_" -ForegroundColor Red
}

# ============================================
# 3. Backup de Configuración
# ============================================
Write-Host "`n[3/3] Backup de Configuración..." -ForegroundColor Yellow

try {
    $configFiles = @(".env", "docker-compose.yml", "scripts/init_db.sql")
    $configBackup = Join-Path $backupPath "config"
    New-Item -ItemType Directory -Path $configBackup | Out-Null
    
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Copy-Item $file $configBackup
            Write-Host "[OK] $file" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "[ERROR] Error en backup de configuración: $_" -ForegroundColor Red
}

# ============================================
# 4. Limpieza de Backups Antiguos
# ============================================
Write-Host "`nLimpiando backups antiguos (más de $RetentionDays días)..." -ForegroundColor Yellow

try {
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $oldBackups = Get-ChildItem -Path $BackupDir -Filter "backup_auto_*" -Directory | 
                  Where-Object { $_.CreationTime -lt $cutoffDate }
    
    if ($oldBackups) {
        foreach ($backup in $oldBackups) {
            Remove-Item -Path $backup.FullName -Recurse -Force
            Write-Host "[DEL] $backup" -ForegroundColor Gray
        }
        Write-Host "[OK] $($oldBackups.Count) backups antiguos eliminados" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No hay backups antiguos para eliminar" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ERROR] Error en limpieza: $_" -ForegroundColor Red
}

# ============================================
# Resumen
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Backup Completado" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Ubicación: $backupPath" -ForegroundColor Cyan
Write-Host "Tamaño: $(Get-ChildItem $backupPath -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { "{0:N2} MB" -format ($_.Sum / 1MB) })" -ForegroundColor Cyan
Write-Host "Retención: $RetentionDays días`n" -ForegroundColor Cyan

if ($Auto) {
    Write-Host "[AUTO] Modo automático completado" -ForegroundColor Green
} else {
    Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
    Read-Host
}
