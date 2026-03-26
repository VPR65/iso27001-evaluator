# ¿Cómo funciona la Inteligencia Artificial en tu Proyecto?

Este documento explica de forma sencilla cómo se integran los modelos de IA en tu sistema de evaluación ISO 27001, diferenciando entre las herramientas de desarrollo y el producto final.

---

## 1. El Esquema General (Diagrama Visual)

Imagina dos mundos separados que colaboran: **El Desarrollo** (donde estamos ahora) y **La Aplicación en Producción** (lo que usarán tus clientes).

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│  MUNDO 1: DESARROLLO (Aquí y Ahora)                                           │
│  "Donde se construye el coche"                                                │
│                                                                               │
│  TÚ <───> [ ASISTENTE QWEN 3.5 (397B) ] <───> Código Fuente                  │
│           (Chat, Explicaciones, Lógica)                                       │
│                                                                               │
│  • Yo soy Qwen, tu asistente virtual.                                         │
│  • Te ayudo a escribir el código, pero NO estoy dentro del software final.    │
│  • Mi trabajo termina cuando el código se guarda.                             │
└───────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ (El código se guarda y se despliega)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│  MUNDO 2: LA APLICACIÓN EN PRODUCCIÓN (Tu Software)                           │
│  "El coche en la carretera"                                                   │
│                                                                               │
│  Usuario Final ──> [ Tu Web App ] ──> [ NVIDIA NIM Cloud ] ──> IA             │
│                     (FastAPI)            (Servidor Externo)    (Llama 3.1)    │
│                                                                               │
│  • Cuando un usuario evalúa un control, tu app "consulta" a la IA.            │
│  • La IA que responde es Llama 3.1 (de Meta), no yo (Qwen).                   │
│  • Ocurre en tiempo real a través de internet.                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Los Dos "Cerebros" Involucrados

Es vital no confundir las dos inteligencias artificiales que aparecen en este proyecto:

| Característica | **1. Tu Asistente (Qwen 3.5)** | **2. El Motor de tu App (Llama 3.1)** |
| :--- | :--- | :--- |
| **¿Qué es?** | Un modelo de Alibaba Cloud muy potente. | Un modelo de Meta (Facebook) especializado. |
| **¿Dónde está?** | En este chat (CLI/GUI). | En los servidores de **NVIDIA Cloud**. |
| **¿Cuándo se usa?** | Cuando tú me pides ayuda o código. | Cuando un usuario final usa tu web para analizar controles. |
| **¿Para qué sirve?** | Para crear la aplicación. | Para dar valor al cliente final (analizar normas ISO). |
| **Tamaño** | 397 Mil Millones de parámetros. | 70 Mil Millones de parámetros. |

> **Analogía del Arquitecto:**
> *   **Qwen (Yo):** Soy el **Arquitecto** que diseña los planos y escribe las instrucciones.
> *   **Llama 3.1:** Es el **Ingeniero Experto** que vive dentro del edificio terminado y resuelve dudas a los inquilinos.

---

## 3. Flujo de Trabajo Paso a Paso

Así es como viaja la información cuando la IA se pone en marcha en tu aplicación:

### Paso 1: El Disparador
Un usuario en tu web (`iso27001-qa.onrender.com`) hace clic en **"Analizar con IA"** en un control de seguridad.

### Paso 2: La Solicitud (Tu App -> NVIDIA)
Tu aplicación (código Python que yo escribí) toma la descripción del control y la respuesta del usuario, y envía un mensaje secreto a **NVIDIA NIM Cloud**.

```text
[ Tu App ] --(API Key)--> "Hola NVIDIA, ¿este control está bien redactado?"
```

### Paso 3: El Procesamiento (La Nube de NVIDIA)
NVIDIA recibe la pregunta y despierta al modelo **Llama 3.1 70B**. Este modelo lee la norma ISO 27001 (que "aprendió" en su entrenamiento) y genera una respuesta experta.

### Paso 4: La Respuesta (NVIDIA -> Tu App)
NVIDIA devuelve el análisis a tu web en segundos.

```text
[ NVIDIA ] --(Resultado)--> "El control es correcto, pero sugiero añadir evidencia física."
```

### Paso 5: El Resultado Final
El usuario ve el consejo experto en su pantalla, como si un auditor experto estuviera revisándolo.

---

## 4. ¿Por qué usamos NVIDIA y Llama 3.1?

No usamos cualquier IA, elegimos esta combinación por razones técnicas y de negocio:

1.  **Privacidad y Seguridad:** Al usar NVIDIA NIM, los datos viajan cifrados y se procesan en infraestructura empresarial, no en servidores públicos gratuitos.
2.  **Especialización:** Llama 3.1 70B es excelente siguiendo instrucciones estrictas (formato JSON) y razonando sobre normas técnicas, algo crucial para auditorías ISO.
3.  **Velocidad:** La infraestructura de NVIDIA está optimizada para responder en milisegundos, dando una experiencia de usuario fluida.

---

## 5. Configuración Actual

Actualmente, tu aplicación está configurada en el archivo `app/ai_service.py` para usar:

*   **Proveedor:** NVIDIA NIM
*   **Modelo:** `meta/llama-3.1-70b-instruct` (Llama 3.1 de 70B)
*   **Función:** Analizar controles, generar recomendaciones y redactar resúmenes ejecutivos.

> **Nota:** Si en el futuro deseas cambiar a un modelo más potente (como Llama 3.1 405B) o de otra marca (como Mistral), solo es cuestión de cambiar una línea de configuración en el código.
