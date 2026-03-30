#!/bin/sh
# Inicialización de Ollama - Descarga modelos si no existen

echo "Iniciando script de inicialización de Ollama..."

# Esperar a que Ollama esté listo
sleep 5

# Modelos por defecto para instalar
DEFAULT_MODELS="llama3.1:latest qwen2:7b phi3:mini"

# Verificar si ya hay modelos
existing_models=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -c '"name"' || echo "0")

if [ "$existing_models" -eq "0" ]; then
    echo "No hay modelos instalados. Instalando modelos por defecto..."
    
    for model in $DEFAULT_MODELS; do
        echo "Descargando modelo: $model"
        ollama pull "$model"
        
        if [ $? -eq 0 ]; then
            echo "✓ Modelo $model instalado correctamente"
        else
            echo "✗ Error al instalar $model (continuando...)"
        fi
    done
else
    echo "Ya existen modelos instalados ($existing_models encontrados). Saltando descarga."
fi

echo "Inicialización de Ollama completada."
