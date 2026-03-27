# Configuración del Modelo de IA

## Vista Rápida

**Para cambiar el modelo de IA:**

1. **Desde la GUI (Recomendado)**:
   - Ve a `/admin/ai-config` (solo superadmin)
   - Selecciona el proveedor (NVIDIA o Ollama)
   - Elige el modelo
   - Haz clic en "Guardar Configuración"

2. **Desde variables de ambiente**:
   ```bash
   AI_MODE=nvidia  # o 'ollama'
   AI_MODEL=meta/llama-3.1-70b-instruct
   ```

## Modelos Disponibles

### NVIDIA NIM (Cloud)
| Modelo | Uso Recomendado |
|--------|-----------------|
| Llama 3.1 70B Instruct | **Default** - Evaluación ISO 27001 |
| Llama 3.1 405B Instruct | Tareas complejas |
| Mistral Large 2 | Alternativa a Llama |
| Mixtral 8x22B | Modelos expertos |
| Gemma 2 27B | Google AI |

### Ollama (Local)
| Modelo | Uso Recomendado |
|--------|-----------------|
| llama3.2 | **Default** - Privacidad total |
| mistral | Alternativa ligera |
| llama3.1 | Compatibilidad |

## Pasos para Configurar

### Opción 1: GUI (Recomendado)

1. Inicia sesión como **superadmin**
2. Ve al menú **Configuración IA** (nuevo en el menú admin)
3. Selecciona el proveedor:
   - **NVIDIA NIM**: Requiere `NVIDIA_API_KEY` en `.env`
   - **Ollama**: Requiere Ollama instalado localmente
4. Elige el modelo de la lista
5. Haz clic en **Guardar Configuración**
6. Reinicia el servidor si es necesario

### Opción 2: Variables de Ambiente

1. Edita `.env`:
   ```bash
   # Para NVIDIA (Cloud)
   AI_MODE=nvidia
   AI_MODEL=meta/llama-3.1-70b-instruct
   NVIDIA_API_KEY=tu_api_key_aqui
   
   # Para Ollama (Local)
   AI_MODE=ollama
   AI_LOCAL_URL=http://localhost:11434
   AI_LOCAL_MODEL=llama3.2
   ```

2. Reinicia la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

## Verificar Configuración

### Desde la GUI
- Ve a `/admin/ai-config`
- Verifica el estado: "IA Habilitada" o "IA No Configurada"

### Desde API
```bash
curl http://localhost:8000/api/ai/models
```

### Desde CLI
```bash
python -c "from app.config import AI_MODE, AI_MODEL; print(f'{AI_MODE}/{AI_MODEL}')"
```

## Solución de Problemas

### Error: "NVIDIA API key not configured"
- Verifica que `NVIDIA_API_KEY` esté en `.env`
- Obtén tu API key en https://build.nvidia.com/

### Error: "Modelo no válido"
- Solo puedes usar modelos de la lista en `AVAILABLE_MODELS`
- Verifica la ortografía del modelo

### Ollama no responde
- Asegúrate de que Ollama esté corriendo: `ollama serve`
- Verifica la URL: `AI_LOCAL_URL=http://localhost:11434`
- Prueba el modelo: `ollama run llama3.2`

## Modelos Recomendados

| Caso de Uso | Modelo Recomendado | Proveedor |
|-------------|-------------------|-----------|
| Evaluación ISO 27001 | Llama 3.1 70B | NVIDIA |
| Privacidad total | Llama 3.2 | Ollama Local |
| Bajo costo | Llama 3.2 | Ollama Local |
| Máxima precisión | Llama 3.1 405B | NVIDIA |

## Cambios Recientes (v1.7.3)

- ✅ Selector de modelos en GUI
- ✅ Soporte multi-proveedor (NVIDIA + Ollama)
- ✅ Cambio dinámico sin reiniciar
- ✅ 8 modelos disponibles
- ✅ Auditoría de cambios de configuración

## Documentación Relacionada

- `AI_STRATEGY.md` - Estrategia de IA
- `PROJECT_STATUS.md` - Estado del proyecto
- `.env.example` - Variables de ambiente

---

**Última actualización:** 2026-03-27  
**Versión:** v1.7.3
