# 🚀 Despliegue a Producción - v2.0.0

**ISO 27001 & ITIL Evaluator**  
**Versión:** v2.0.0  
**Fecha:** 2026-03-30  
**Estado:** ✅ Listo para producción

---

## ✅ Pre-Checklist (Completado)

- [x] Tests passing (100%)
- [x] Documentación actualizada
- [x] CHANGELOG.md actualizado
- [x] Tag v2.0.0 creado
- [x] Release notes generadas
- [x] Push a remoto completado
- [ ] Deploy a producción
- [ ] Verificación post-deploy

---

## 📋 Opciones de Despliegue

### Opción 1: Oracle Cloud Free Tier (Recomendada)

**Costo:** $0/mes (Free Tier)  
**Recursos:** 4 OCPUs, 24GB RAM, 200GB storage

#### Pasos:

1. **Crear cuenta Oracle Cloud**
   - Ir a https://oracle.com/cloud/free
   - Crear cuenta gratuita

2. **Crear VM Ampere A1**
   - Shape: VM.Standard.A1.Flex
   - OCPUs: 4, Memoria: 24GB
   - OS: Ubuntu 22.04

3. **Configurar firewall**
   ```bash
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 8000/tcp  # App
   sudo ufw allow 11434/tcp # Ollama (opcional)
   sudo ufw enable
   ```

4. **Instalar dependencias**
   ```bash
   # Python
   sudo apt update
   sudo apt install python3-pip python3-venv -y
   
   # Git
   sudo apt install git -y
   
   # Node.js (opcional)
   sudo apt install nodejs npm -y
   ```

5. **Clonar repositorio**
   ```bash
   git clone https://github.com/tu-usuario/iso27001-evaluator.git
   cd iso27001-evaluator
   ```

6. **Crear entorno virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

7. **Configurar variables de ambiente**
   ```bash
   cp .env.docker .env
   # Editar .env con valores de producción
   ```

8. **Instalar Ollama (opcional)**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.1:latest
   ```

9. **Crear servicio systemd**
   ```bash
   sudo nano /etc/systemd/system/iso27001.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=ISO 27001 Evaluator
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/iso27001-evaluator
   ExecStart=/home/ubuntu/iso27001-evaluator/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

10. **Iniciar servicio**
    ```bash
    sudo systemctl enable iso27001
    sudo systemctl start iso27001
    sudo systemctl status iso27001
    ```

11. **Verificar**
    ```bash
    curl http://localhost:8000/health
    ```

---

### Opción 2: Docker Compose (Local/On-Premise)

**Requisitos:** Docker, Docker Compose

#### Pasos:

1. **Copiar archivo de ejemplo**
   ```bash
   cp docker-compose.yml.example docker-compose.yml
   cp .env.docker .env
   ```

2. **Editar variables**
   ```bash
   nano .env
   # Ajustar SECRET_KEY, DATABASE_URL, etc.
   ```

3. **Construir y levantar**
   ```bash
   docker-compose up -d --build
   ```

4. **Verificar**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

5. **Acceder**
   - App: http://localhost:8000
   - DB: localhost:5432
   - Ollama: localhost:11434

---

### Opción 3: Render.com (Cloud Gratuito)

**Costo:** $0/mes (Free Tier)  
**Limitaciones:** 512MB RAM, sleep después de inactividad

#### Pasos:

1. **Crear cuenta en Render**
   - Ir a https://render.com
   - Sign up con GitHub

2. **Crear Web Service**
   - New > Web Service
   - Conectar repositorio

3. **Configurar build**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Variables de ambiente**
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=tu_secreto_aqui
   AI_MODE=nvidia (usar API externa)
   ```

5. **Deploy**
   - Click en "Create Web Service"
   - Esperar deployment

---

## 🔧 Post-Deploy Checklist

### Inmediato (primeros 5 minutos)

- [ ] Verificar health check: `curl http://tu-domain:8000/health`
- [ ] Acceder desde navegador
- [ ] Loguearse con admin@acme.com / admin123
- [ ] Verificar conexión a BD
- [ ] Probar endpoint de IA (si aplica)

### Primeros 30 minutos

- [ ] Configurar backups automáticos
  ```bash
  python scripts/auto_backup.py
  ```
  
- [ ] Programar monitoreo
  ```bash
  # Cada 5 minutos
  python scripts/monitor.py
  ```

- [ ] Verificar logs
  ```bash
  tail -f logs/app.log
  tail -f logs/monitor.log
  ```

### Primeras 24 horas

- [ ] Revisar métricas de uso
- [ ] Verificar backups generados
- [ ] Monitorear consumo de recursos
- [ ] Revisar alerts generadas

---

## 📊 Monitoreo Post-Deploy

### Comandos Esenciales

```bash
# Estado del sistema
python scripts/monitor.py

# Alertas activas
python scripts/alert_manager.py status

# Verificación rápida
python scripts/quick_check.py

# Logs en tiempo real
tail -f logs/app.log
```

### Métricas a Vigilar

| Métrica | Umbral Alerta | Acción |
|---------|---------------|--------|
| CPU | >80% | Revisar procesos |
| RAM | >90% | Escalar o limpiar |
| Disco | >90% | Limpiar backups viejos |
| Backups | <1 en 24h | Revisar script |
| Uptime | <99% | Investigar caídas |

---

## 🚨 Solución de Problemas Comunes

### La app no inicia

```bash
# Verificar logs
journalctl -u iso27001 -n 50

# Verificar puerto
sudo netstat -tulpn | grep 8000

# Reiniciar servicio
sudo systemctl restart iso27001
```

### Backups fallan

```bash
# Verificar espacio
df -h

# Espacio disponible
python scripts/monitor.py | grep Disco

# Limpiar backups viejos
python scripts/backup.py clean_old_backups --days 7
```

### Ollama no responde

```bash
# Verificar servicio
systemctl status ollama

# Reiniciar
ollama serve

# Verificar modelos
ollama list
```

---

## 📞 Soporte

### Documentación
- `RELEASE_NOTES_v2.0.0.md` - Release notes
- `QUICKSTART.md` - Guía rápida
- `docs/MONITORING.md` - Monitoreo
- `docs/PROJECT_STATUS_SUMMARY.md` - Estado

### Comandos de Diagnóstico
```bash
python scripts/quick_check.py  # Check rápido
python scripts/monitor.py      # Estado completo
python scripts/qa_test.py      # Tests
```

### Logs
- `logs/app.log` - Aplicación
- `logs/monitor.log` - Monitoreo
- `logs/alerts.log` - Alertas

---

## ✅ Confirmación de Éxito

El deployment fue exitoso si:

- [x] Health check responde: `{"status":"healthy"}`
- [x] Login funciona con admin@acme.com
- [x] Dashboard carga correctamente
- [x] Backups se generan automáticamente
- [x] Monitoreo reporta "TODO OK"
- [x] No hay alertas críticas

---

**¡Felicidades! Tu sistema ISO 27001 & ITIL Evaluator v2.0.0 está en producción.**

**Siguiente paso:** Configurar alertas por email y monitoreo continuo.

---

*Documento generado: 2026-03-30*  
*Versión: v2.0.0*  
*Commit: aec7ee8*
