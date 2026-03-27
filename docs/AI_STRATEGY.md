# 🤖 ESTRATEGIA DE IA - ISO 27001 Evaluator

**Fecha:** 27 de Marzo de 2026  
**Versión:** 1.0.0  
**Estado:** En Implementación

---

## 🎯 Contexto del Proyecto

Nuestro proyecto tiene requisitos ESPECÍFICOS:

1. **Soberanía de Datos** - No podemos enviar código sensible a APIs externas
2. **Costo Cero** - Presupuesto $0 para IA
3. **Código Existente** - ~15,000 líneas de código base
4. **Lógica Compleja** - ISO 27001, ITIL v4, auditoría

---

## 📊 Evaluación de Modelos Disponibles

### Tier 1: Modelos "Top" (Pago)
| Modelo | Calidad | Costo | Soberanía | Uso Recomendado |
|--------|---------|-------|-----------|-----------------|
| GPT-5.2 | ⭐⭐⭐⭐⭐ | $$$ | ❌ Externo | Arquitectura crítica |
| Claude Opus 4.5 | ⭐⭐⭐⭐⭐ | $$$ | ❌ Externo | Refactorización grande |
| Claude Sonnet 4.5 | ⭐⭐⭐⭐ | $$ | ❌ Externo | Uso diario intensivo |
| Gemini 3 Pro | ⭐⭐⭐⭐ | $$ | ❌ Externo | Integraciones GCP |

### Tier 2: Modelos Open/Low-Cost
| Modelo | Calidad | Costo | Soberanía | Uso Recomendado |
|--------|---------|-------|-----------|-----------------|
| NVIDIA NIM (Llama 3.2) | ⭐⭐⭐ | $0 | ✅ Local | **DEFAULT** |
| GLM-5 | ⭐⭐⭐ | $ | ❌ Externo | Tareas repetitivas |
| Kimi K2.5 | ⭐⭐⭐ | $ | ❌ Externo | Tests unitarios |
| MiniMax M2.5-2.7 | ⭐⭐⭐ | $ | ❌ Externo | Boilerplate |

---

## 🎯 Estrategia Híbrida Implementada

### Nivel 1: IA Local (Default) - NVIDIA NIM
**Modelo:** Llama 3.2 3B o Mistral 7B  
**Ubicación:** Oracle Cloud Free Tier (nuestro control)  
**Casos de uso:**
- ✅ Generar código repetitivo
- ✅ Tests unitarios
- ✅ Documentación
- ✅ Refactorización pequeña
- ✅ Análisis de archivos individuales

**Configuración:**
```bash
AI_MODE=ollama
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.2
```

### Nivel 2: IA Externa (Opcional, bajo demanda)
**Modelo:** Claude Sonnet 4.5 o GPT-5.2  
**Ubicación:** API externa (solo si el cliente autoriza)  
**Casos de uso:**
- ⚠️ Refactorización de arquitectura completa
- ⚠️ Migraciones grandes
- ⚠️ Revisión de seguridad profunda

**Configuración:**
```bash
AI_MODE=nvidia  # o anthropic/openai
NVIDIA_API_KEY=xxx  # o ANTHROPIC_API_KEY
ALLOW_EXTERNAL_AI=true  # Solo si cliente autoriza
```

### Nivel 3: Sin IA (Manual)
**Casos de uso:**
- ❌ Decisiones de negocio
- ❌ Análisis de repositorio completo
- ❌ Decisiones de arquitectura crítica
- ❌ Revisión final de seguridad

---

## 📋 Matriz de Decisión

| Tarea | Modelo Recomendado | Razón |
|-------|-------------------|-------|
| Generar CRUD básico | NVIDIA NIM | Rápido, local, free |
| Tests unitarios | NVIDIA NIM | Suficiente calidad |
| Documentar endpoint | NVIDIA NIM | Contexto largo |
| Refactorizar función | NVIDIA NIM | Análisis local |
| Migrar DB completa | Claude/GPT | Estrategia compleja |
| Diseñar arquitectura | Claude Opus | Visión global |
| Revisión seguridad | Claude/GPT | Profundidad |
| Decisión de negocio | HUMANO | No delegar |

---

## 🔧 Implementación Técnica

### Variables de Ambiente
```bash
# Modo de IA
AI_MODE=local  # local | nvidia | anthropic | openai

# IA Local (Recomendado)
AI_LOCAL_URL=http://localhost:11434
AI_LOCAL_MODEL=llama3.2
AI_LOCAL_TIMEOUT=60

# IA Externa (Opcional)
NVIDIA_API_KEY=  # Solo si AI_MODE=nvidia
ANTHROPIC_API_KEY=  # Solo si AI_MODE=anthropic
OPENAI_API_KEY=  # Solo si AI_MODE=openai

# Seguridad
ALLOW_EXTERNAL_AI=false  # Default: false (soberanía)
ENCRYPT_AI_REQUESTS=true  # Encriptar requests salientes
```

### Switch de IA en Código
```python
def get_ai_service():
    """Factory para obtener el servicio de IA según configuración"""
    
    if settings.AI_MODE == 'local':
        return OllamaService(
            base_url=settings.AI_LOCAL_URL,
            model=settings.AI_LOCAL_MODEL
        )
    
    elif settings.AI_MODE == 'nvidia' and settings.NVIDIA_API_KEY:
        return NvidiaService(
            api_key=settings.NVIDIA_API_KEY,
            model='meta/llama-3.1-70b-instruct'
        )
    
    elif settings.AI_MODE == 'anthropic' and settings.ANTHROPIC_API_KEY:
        return AnthropicService(
            api_key=settings.ANTHROPIC_API_KEY,
            model='claude-sonnet-4-5'
        )
    
    else:
        return None  # IA deshabilitada
```

---

## ⚠️ Consideraciones de Seguridad

### Datos Sensibles
- ✅ **NUNCA** enviar: passwords, API keys, datos de clientes
- ✅ **Siempre** encriptar requests si se usa IA externa
- ✅ **Validar** que el cliente autoriza IA externa

### Compliance ISO 27001
- ✅ Auditoría de todos los requests de IA
- ✅ Logs de qué código se envía y a qué modelo
- ✅ Política de uso de IA documentada
- ✅ Evaluación de riesgos de proveedor de IA

---

## 📈 Métricas de Uso

| Métrica | Objetivo | Real |
|---------|----------|------|
| % Código con IA local | 80% | - |
| % Código con IA externa | <5% | - |
| % Código manual | 15% | - |
| Costo mensual IA | $0 | $0 |
| Requests/día | 50-100 | - |

---

## 🎯 Próximos Pasos

1. **Implementar factory de IA** (2026-03-28)
2. **Configurar Oracle + Ollama** (2026-03-29)
3. **Tests de calidad por modelo** (2026-03-30)
4. **Documentar políticas de uso** (2026-04-01)
5. **Capacitar equipo** (2026-04-02)

---

**Fin del Documento**
