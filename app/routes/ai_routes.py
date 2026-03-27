"""
AI Routes - Endpoints for AI-powered evaluation features
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from app.auth import get_current_user, SESSION_COOKIE_NAME
from app.models import UserRole
from app.ai_service import get_ai_service
from app.database import engine
from sqlmodel import Session, select
from app.models import Evaluation, ControlResponse, ControlDefinition, Norma, Client
from app.config import AI_MODE, AI_MODEL, AVAILABLE_MODELS, AI_LOCAL_URL, AI_LOCAL_MODEL

router = APIRouter(prefix="/api/ai", tags=["ai"])


def require_auth(request: Request):
    """Verify user is authenticated"""
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    return user


class AnalyzeControlRequest(BaseModel):
    evaluation_id: str
    control_id: str


class GenerateSummaryRequest(BaseModel):
    evaluation_id: str
    include_recommendations: bool = True


@router.get("/status")
def ai_status(request: Request):
    """Check if AI service is configured and available (legacy endpoint)"""
    require_auth(request)
    service = get_ai_service()
    return {
        "enabled": service.enabled,
        "message": "NVIDIA NIM API configurada"
        if service.enabled
        else "Configure NVIDIA_API_KEY para activar IA",
    }


@router.get("/status/detailed")
async def ai_status_detailed(request: Request):
    """
    Get detailed AI availability status with fallback logic.
    Returns current AI provider (Ollama → NVIDIA → None) with visual indicators.
    """
    require_auth(request)
    service = get_ai_service()
    status = await service.get_ai_status()
    return status


@router.get("/models")
def get_available_models(request: Request):
    """Get list of available AI models and current configuration"""
    require_auth(request)
    return {
        "models": AVAILABLE_MODELS,
        "current_model": AI_MODEL,
        "ai_mode": AI_MODE,
        "local_url": AI_LOCAL_URL,
        "local_model": AI_LOCAL_MODEL,
    }


class SetModelRequest(BaseModel):
    model: str
    ai_mode: Optional[str] = None


@router.post("/set-model")
def set_ai_model(request_data: SetModelRequest, request: Request):
    """Set the current AI model to use"""
    require_auth(request)

    model_id = request_data.model
    ai_mode = request_data.ai_mode or AI_MODE

    valid_models = [m["id"] for m in AVAILABLE_MODELS]
    if model_id not in valid_models:
        raise HTTPException(
            status_code=400,
            detail=f"Modelo no válido. Modelos disponibles: {', '.join(valid_models)}",
        )

    import os
    from dotenv import set_key

    try:
        set_key(".env", "AI_MODEL", model_id)
        if ai_mode:
            set_key(".env", "AI_MODE", ai_mode)

        return JSONResponse(
            content={
                "success": True,
                "message": f"Modelo cambiado a {model_id}. Reinicie la servidor para aplicar.",
                "model": model_id,
                "ai_mode": ai_mode,
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al configurar el modelo: {str(e)}"
        )


@router.post("/analyze-control")
def analyze_control(request_data: AnalyzeControlRequest, request: Request):
    """Analyze a single control response using AI"""
    require_auth(request)

    with Session(engine) as session:
        # Get control definition
        control_def = session.get(ControlDefinition, request_data.control_id)
        if not control_def:
            raise HTTPException(status_code=404, detail="Control no encontrado")

        # Get response if exists
        response = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == request_data.evaluation_id,
                ControlResponse.control_definition_id == request_data.control_id,
            )
        ).first()

        response_text = response.response_text if response else "Sin responder"

        service = get_ai_service()
        result = service.analyze_control_response(
            control_code=control_def.code,
            control_title=control_def.title,
            control_description=control_def.description,
            response=response_text,
        )

        return JSONResponse(content=result)


@router.post("/generate-summary")
def generate_summary(request_data: GenerateSummaryRequest, request: Request):
    """Generate executive summary for an evaluation"""
    require_auth(request)

    with Session(engine) as session:
        evaluation = session.get(Evaluation, request_data.evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")

        norma = session.get(Norma, evaluation.norma_id) if evaluation.norma_id else None
        client = (
            session.get(Client, evaluation.client_id) if evaluation.client_id else None
        )

        # Get all control responses
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation.id
            )
        ).all()

        # Get total controls for this norma
        total_controls = 0
        if norma:
            total_controls = session.exec(
                select(ControlDefinition).where(ControlDefinition.norma_id == norma.id)
            ).count()

        # Count by status
        compliant = 0
        non_compliant = 0
        in_progress = 0

        controls_summary = []

        for resp in responses:
            ctrl = session.get(ControlDefinition, resp.control_definition_id)
            status = resp.status.value if resp.status else "in_progress"

            if status == "compliant":
                compliant += 1
            elif status == "non_compliant":
                non_compliant += 1
                controls_summary.append(
                    {
                        "code": ctrl.code if ctrl else "?",
                        "title": ctrl.title if ctrl else "Sin título",
                        "status": status,
                        "finding": resp.finding or "No conforme",
                    }
                )
            else:
                in_progress += 1

        service = get_ai_service()

        # Generate summary
        summary = service.generate_executive_summary(
            evaluation_name=evaluation.name,
            client_name=client.name if client else "N/A",
            norma_name=norma.name if norma else "N/A",
            total_controls=total_controls,
            compliant_count=compliant,
            non_compliant_count=non_compliant,
            in_progress_count=in_progress,
            controls_summary=controls_summary,
        )

        # Generate recommendations if requested
        recommendations = []
        if request_data.include_recommendations and non_compliant > 0:
            recommendations = service.generate_recommendations(controls_summary)

        return JSONResponse(
            content={
                "summary": summary,
                "stats": {
                    "total_controls": total_controls,
                    "compliant": compliant,
                    "non_compliant": non_compliant,
                    "in_progress": in_progress,
                    "compliance_rate": round(compliant / total_controls * 100, 1)
                    if total_controls > 0
                    else 0,
                },
                "recommendations": recommendations,
            }
        )


@router.get("/control-guidance/{control_id}")
def get_control_guidance(control_id: str, request: Request):
    """Get AI-generated guidance for filling out a control"""
    require_auth(request)

    with Session(engine) as session:
        control = session.get(ControlDefinition, control_id)
        if not control:
            raise HTTPException(status_code=404, detail="Control no encontrado")

        service = get_ai_service()
        guidance = service.generate_control_guidance(
            control_code=control.code, control_title=control.title
        )

        return JSONResponse(
            content={
                "control_id": control_id,
                "code": control.code,
                "title": control.title,
                "guidance": guidance,
            }
        )
