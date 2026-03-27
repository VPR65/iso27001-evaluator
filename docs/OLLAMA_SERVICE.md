# Servicio de IA Local con Ollama

Este documento describe la implementación del servicio de IA local utilizando Ollama para el proyecto ISO 27001.

## Requisitos

- Ollama instalado localmente
- Modelo de IA descargado (por ejemplo, llama2, mistral, etc.)

## Implementación

1. Verificar que Ollama esté en ejecución:
   ```bash
   ollama --version
   ```

2. Listar modelos disponibles:
   ```bash
   ollama list
   ```

3. Descargar modelo si no está disponible:
   ```bash
   ollama pull llama2
   ```

4. Iniciar el servicio de Ollama:
   ```bash
   ollama serve
   ```

5. Probar el modelo:
   ```bash
   curl http://localhost:11434/api/generate -d "{\"model\":\"llama2\",\"prompt\":\"hello\"}"
   ```