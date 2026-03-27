"""
AI Service - Multi-Provider Integration (NVIDIA, Ollama, Anthropic, OpenAI)
Provides AI-powered analysis for ISO 27001 evaluations
Supports on-demand AI with automatic fallback: Ollama → NVIDIA → None
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import (
    AI_MODE,
    AI_MODEL,
    AI_LOCAL_URL,
    AI_LOCAL_MODEL,
    NVIDIA_API_KEY,
    AVAILABLE_MODELS,
)

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1"


class AIService:
    """Service for AI-powered evaluation analysis with on-demand fallback"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or NVIDIA_API_KEY
        self.ai_mode = AI_MODE
        self.model = model or AI_MODEL
        self.local_url = AI_LOCAL_URL
        self.local_model = AI_LOCAL_MODEL
        self.enabled = bool(self.api_key) if self.ai_mode == "nvidia" else True
        self._availability_cache = None
        self._cache_timestamp = None

    def _get_model_to_use(self, model: Optional[str] = None) -> str:
        """Get the model to use based on AI mode"""
        if model:
            return model
        if self.ai_mode == "ollama":
            return self.local_model
        return self.model

    async def check_ollama_availability(self) -> Dict[str, Any]:
        """
        Check if Ollama is available and responding.
        Returns dict with availability status, models, and error message if any.
        Caches result for 5 seconds to avoid excessive polling.
        """
        import time

        current_time = time.time()

        # Return cached result if less than 5 seconds old
        if (
            self._availability_cache
            and self._cache_timestamp
            and current_time - self._cache_timestamp < 5
        ):
            return self._availability_cache

        try:
            import httpx

            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.local_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    result = {
                        "available": True,
                        "models": models,
                        "model_count": len(models),
                        "error": None,
                        "provider": "ollama",
                    }
                    self._availability_cache = result
                    self._cache_timestamp = current_time
                    return result
                else:
                    result = {
                        "available": False,
                        "models": [],
                        "model_count": 0,
                        "error": f"Ollama returned status {response.status_code}",
                        "provider": "ollama",
                    }
                    self._availability_cache = result
                    self._cache_timestamp = current_time
                    return result
        except Exception as e:
            result = {
                "available": False,
                "models": [],
                "model_count": 0,
                "error": str(e),
                "provider": "ollama",
            }
            self._availability_cache = result
            self._cache_timestamp = current_time
            return result

    async def check_nvidia_availability(self) -> Dict[str, Any]:
        """
        Check if NVIDIA NIM API is available.
        Returns dict with availability status and error message if any.
        """
        if not self.api_key:
            return {
                "available": False,
                "error": "NVIDIA API key not configured",
                "provider": "nvidia",
            }

        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # Simple test call to NVIDIA API
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
            }

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{NVIDIA_API_URL}/chat/completions",
                    headers=headers,
                    json=test_payload,
                )

                if response.status_code in [200, 400]:  # 400 is OK for test
                    return {"available": True, "error": None, "provider": "nvidia"}
                else:
                    return {
                        "available": False,
                        "error": f"NVIDIA API returned status {response.status_code}",
                        "provider": "nvidia",
                    }
        except Exception as e:
            return {"available": False, "error": str(e), "provider": "nvidia"}

    async def get_ai_status(self) -> Dict[str, Any]:
        """
        Get comprehensive AI availability status with fallback logic.
        Priority: Ollama (Local) → NVIDIA (Cloud) → None

        Returns:
            Dict with status, icon, model, message, and privacy info
        """
        # Try Ollama first (local preferred)
        ollama_status = await self.check_ollama_availability()
        if ollama_status["available"]:
            return {
                "status": "local",
                "icon": "🟢",
                "model": self.local_model,
                "message": "IA Local Activa",
                "privacy": "100% local - Datos no salen",
                "provider": "ollama",
                "available": True,
            }

        # Try NVIDIA as fallback
        if self.api_key:
            nvidia_status = await self.check_nvidia_availability()
            if nvidia_status["available"]:
                return {
                    "status": "nvidia",
                    "icon": "🟡",
                    "model": self.model,
                    "message": "IA Externa (NVIDIA)",
                    "privacy": "⚠️ Datos se envían a NVIDIA",
                    "provider": "nvidia",
                    "available": True,
                }

        # No AI available
        return {
            "status": "none",
            "icon": "🔴",
            "model": "Ninguno",
            "message": "Sin IA disponible",
            "privacy": "Evaluación manual",
            "provider": "none",
            "available": False,
            "instructions": "Inicia Ollama con: ollama serve",
        }

    def _call_nvidia_api(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """Make a call to NVIDIA NIM API or local Ollama"""
        model_to_use = self._get_model_to_use(model)

        if self.ai_mode == "ollama":
            return self._call_ollama(messages, model_to_use, temperature)

        if not self.enabled:
            raise ValueError("NVIDIA API key not configured")

        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{NVIDIA_API_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _call_ollama(
        self, messages: list[dict], model: str, temperature: float = 0.3
    ) -> str:
        """Make a call to local Ollama instance"""
        import httpx

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.local_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    def analyze_control_response(
        self,
        control_code: str,
        control_title: str,
        control_description: str,
        response: str,
    ) -> dict:
        """
        Analyze if a control response is adequate and complete.

        Returns:
            dict with: is_adequate (bool), score (int 1-10), issues (list), suggestions (list)
        """
        if not self.enabled:
            return {
                "is_adequate": True,
                "score": 10,
                "issues": [],
                "suggestions": ["AI no disponible - Configure NVIDIA_API_KEY"],
                "analysis": "AI analysis not available",
            }

        system_prompt = """Eres un experto en auditoría ISO 27001. Analiza las respuestas de controles de seguridad y evalúa su calidad.
Responde SOLO con JSON válido en este formato:
{
    "is_adequate": true/false,
    "score": 1-10,
    "issues": ["lista de problemas encontrados"],
    "suggestions": ["lista de sugerencias de mejora"],
    "analysis": "breve explicación del análisis"
}"""

        user_prompt = f"""Analiza este control ISO 27001:

**Código:** {control_code}
**Título:** {control_title}
**Descripción del control:** {control_description}
**Respuesta del evaluador:** {response}

Evalúa si la respuesta es adecuada, completa y si cumple con los requisitos del control."""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            result = self._call_nvidia_api(messages)

            # Try to parse JSON from response
            json_start = result.find("{")
            json_end = result.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(result[json_start:json_end])

            return {
                "is_adequate": True,
                "score": 7,
                "issues": [],
                "suggestions": [],
                "analysis": result[:500],
            }
        except Exception as e:
            return {
                "is_adequate": True,
                "score": 7,
                "issues": [str(e)],
                "suggestions": [],
                "analysis": f"Error en análisis: {str(e)[:200]}",
            }

    def generate_recommendations(self, failed_controls: list[dict]) -> list[dict]:
        """
        Generate recommendations for failed/non-compliant controls.

        Args:
            failed_controls: List of dicts with control info and findings

        Returns:
            List of dicts with recommendations per control
        """
        if not self.enabled:
            return [
                {
                    "control_code": c.get("code", "?"),
                    "recommendation": "Configure NVIDIA_API_KEY para generar recomendaciones con IA",
                    "priority": "high",
                    "estimated_effort": "N/A",
                }
                for c in failed_controls[:5]
            ]

        system_prompt = """Eres un experto en implementación de ISO 27001 y ciberseguridad.
Genera recomendaciones prácticas y priorizadas para remediar controles fallidos.
Responde SOLO con JSON válido - un array de objetos:
[{
    "control_code": "A.5.x.x",
    "recommendation": "descripción clara de la acción a tomar",
    "priority": "high/medium/low",
    "estimated_effort": "bajo/medio/alto",
    "compliance_impact": "impacto en el cumplimiento"
}]"""

        controls_text = "\n\n".join(
            [
                f"**Control {i + 1}:** {c.get('code', '?')} - {c.get('title', '?')}\n"
                f"Estado: {c.get('status', 'N/A')}\n"
                f"Hallazgo: {c.get('finding', 'No conforme')}\n"
                for i, c in enumerate(failed_controls)
            ]
        )

        user_prompt = f"""Genera recomendaciones de remediation para los siguientes controles ISO 27001 que fallaron:

{controls_text}

Para cada control proporciona:
1. recommendation: Acción específica a tomar
2. priority: high (crítico), medium (importante), low (deseable)
3. estimated_effort: bajo (días), medio (semanas), alto (meses)
4. compliance_impact: Cuánto mejora el cumplimiento"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            result = self._call_nvidia_api(messages)

            json_start = result.find("[")
            json_end = result.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(result[json_start:json_end])

            return [{"error": "No se pudo parsear la respuesta", "raw": result[:500]}]
        except Exception as e:
            return [{"error": str(e), "control_code": "?"}]

    def generate_executive_summary(
        self,
        evaluation_name: str,
        client_name: str,
        norma_name: str,
        total_controls: int,
        compliant_count: int,
        non_compliant_count: int,
        in_progress_count: int,
        controls_summary: list[dict],
    ) -> str:
        """
        Generate an executive summary for an evaluation report.

        Returns:
            HTML-formatted executive summary
        """
        if not self.enabled:
            return """
            <div class="ai-summary">
                <h3>Resumen Ejecutivo</h3>
                <p><em>Configure NVIDIA_API_KEY para generar resumen con IA</em></p>
                <div class="summary-stats">
                    <div class="stat"><strong>Total Controles:</strong> {total}</div>
                    <div class="stat"><strong>Conformes:</strong> {compliant}</div>
                    <div class="stat"><strong>No Conformes:</strong> {non_compliant}</div>
                    <div class="stat"><strong>En Progreso:</strong> {in_progress}</div>
                </div>
            </div>
            """.format(
                total=total_controls,
                compliant=compliant_count,
                non_compliant=non_compliant_count,
                in_progress=in_progress_count,
            )

        compliance_rate = (
            (compliant_count / total_controls * 100) if total_controls > 0 else 0
        )

        system_prompt = """Eres un experto en reportes de auditoría ISO 27001.
Genera un resumen ejecutivo profesional en español para un informe de evaluación.
El resumen debe ser formal, claro y orientado a la alta dirección.
Usa formato HTML con tags: <h3>, <p>, <ul>, <li>, <strong>, <em>."""

        user_prompt = f"""Genera un resumen ejecutivo para la siguiente evaluación ISO 27001:

**Evaluación:** {evaluation_name}
**Cliente:** {client_name}
**Norma:** {norma_name}

**Resultados:**
- Total de controles evaluados: {total_controls}
- Controles conformes: {compliant_count}
- Controles no conformes: {non_compliant_count}
- Controles en progreso: {in_progress_count}
- Tasa de cumplimiento: {compliance_rate:.1f}%

**Controles críticos no conformes:**
{chr(10).join([f"- {c.get('code', '?')}: {c.get('title', '?')}" for c in controls_summary[:5]])}

El resumen debe incluir:
1. Título y contexto
2. Hallazgos principales (positivos y negativos)
3. Controles más críticos que requieren atención inmediata
4. Nivel de riesgo general
5. Próximos pasos recomendados
6. Conclusión"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            result = self._call_nvidia_api(messages, temperature=0.5)
            return result
        except Exception as e:
            return f"<p>Error generando resumen: {str(e)}</p>"

    def generate_control_guidance(self, control_code: str, control_title: str) -> str:
        """
        Generate guidance text for filling out a control.

        Returns:
            Guidance text to help evaluators
        """
        if not self.enabled:
            return "Configure NVIDIA_API_KEY para obtener guía del control con IA"

        system_prompt = """Eres un experto en ISO 27001. Proporciona orientación práctica para evaluar y documentar controles.
Sé conciso y práctico. Máximo 3 párrafos."""

        user_prompt = f"""Proporciona orientación para evaluar el control {control_code} - {control_title}.

Incluye:
1. Qué evidencia buscar
2. Preguntas clave para la entrevista/documentación
3. Criterios de conformidad"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            return self._call_nvidia_api(messages, temperature=0.4)
        except Exception as e:
            return f"Error: {str(e)}"


# Singleton instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """Get the AI service singleton"""
    return ai_service
