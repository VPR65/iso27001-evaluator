from fastapi import APIRouter, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from app.models import (
    Evaluation,
    ControlDefinition,
    ControlResponse,
    EvidenceFile,
    AuditLog,
    User,
    UserRole,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.security import verify_csrf_token
from pathlib import Path
import hashlib
import aiofiles

router = APIRouter(prefix="/evaluate/{evaluation_id}", tags=["evaluate"])

MATURITY_LEVELS = {
    0: ("No existe", "El control no esta implementado ni reconocido."),
    1: (
        "Inicial / Ad-hoc",
        "Existe de forma informal, no documentado ni estandarizado.",
    ),
    2: ("Gestionado", "Procesos documentados y aprobados, pero no generalizados."),
    3: ("Definido", "Procesos estandarizados y comunicados en toda la organizacion."),
    4: ("Cuantitativamente gestionado", "Medido y controlado con metricas objetivas."),
    5: ("Optimizado", "Mejora continua basada en metricas y retroalimentacion."),
}


@router.get("/control/{control_id}", response_class=HTMLResponse)
def evaluate_control(request: Request, evaluation_id: str, control_id: str):
    from app.templates_core import render

    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)
        ctrl = session.get(ControlDefinition, control_id)
        if not ctrl:
            raise HTTPException(status_code=404)
        resp = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id,
                ControlResponse.control_id == control_id,
            )
        ).first()
        files = []
        if resp:
            files = session.exec(
                select(EvidenceFile).where(EvidenceFile.response_id == resp.id)
            ).all()
        all_controls = session.exec(
            select(ControlDefinition).order_by(ControlDefinition.code)
        ).all()
        ctrl_ids = [c.id for c in all_controls]
        current_idx = ctrl_ids.index(control_id) if control_id in ctrl_ids else 0
        prev_ctrl = ctrl_ids[current_idx - 1] if current_idx > 0 else None
        next_ctrl = (
            ctrl_ids[current_idx + 1] if current_idx < len(ctrl_ids) - 1 else None
        )

        return render(
            request,
            "evaluate/control.html",
            evaluation=evaluation,
            ctrl=ctrl,
            response=resp,
            files=files,
            maturity_levels=MATURITY_LEVELS,
            prev_ctrl=prev_ctrl,
            next_ctrl=next_ctrl,
            current_idx=current_idx + 1,
            total=len(ctrl_ids),
        )


@router.post("/control/{control_id}/save")
async def save_control(
    request: Request,
    evaluation_id: str,
    control_id: str,
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    maturity = int(form_data.get("maturity") or 0)
    not_applicable = form_data.get("not_applicable") == "true"
    justification = form_data.get("justification", "")
    notes = form_data.get("notes", "")

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)
        from datetime import datetime

    resp = session.exec(
        select(ControlResponse).where(
            ControlResponse.evaluation_id == evaluation_id,
            ControlResponse.control_id == control_id,
        )
    ).first()
    if resp:
        # Guardar valores anteriores para auditoría
        old_maturity = resp.maturity
        old_notes = resp.notes
        old_justification = resp.justification

        # Actualizar valores
        resp.maturity = maturity
        resp.not_applicable = not_applicable
        resp.justification = justification if not_applicable else None
        resp.notes = notes
        resp.updated_at = datetime.utcnow()
        session.add(resp)

        ctrl = session.get(ControlDefinition, control_id)

        # Crear log de auditoría con detalles del cambio
        change_details = f"Control {ctrl.code}: "
        if old_maturity != maturity:
            change_details += f"Madurez {old_maturity} -> {maturity}. "
        if old_notes != notes:
            change_details += f"Notas actualizadas. "
        if not_applicable and justification != old_justification:
            change_details += f"Justificación: {justification[:50]}..."

        session.add(
            AuditLog(
                user_id=user.id,
                action="CONTROL_UPDATED",
                entity_type="control_response",
                entity_id=resp.id,
                details=change_details,
            )
        )
        session.commit()
        return RedirectResponse(
            url=f"/evaluate/{evaluation_id}/control/{control_id}", status_code=302
        )


@router.get("/control/{control_id}/history")
def control_history(
    request: Request,
    evaluation_id: str,
    control_id: str,
):
    """Ver historial de cambios de un control"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)

        # Obtener respuesta
        resp = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id,
                ControlResponse.control_id == control_id,
            )
        ).first()

        if not resp:
            raise HTTPException(status_code=404)

        # Obtener logs de auditoría para esta respuesta
        logs = session.exec(
            select(AuditLog)
            .where(AuditLog.entity_id == str(resp.id))
            .where(AuditLog.entity_type == "control_response")
            .order_by(AuditLog.created_at.desc())
        ).all()

        # Obtener definición del control
        ctrl = session.get(ControlDefinition, control_id)

        return HTMLResponse(
            f"""
            <h3>Historial de Cambios - {ctrl.code}</h3>
            <div class="history-list">
            {
                "".join(
                    [
                        f'''
            <div class="history-item">
                <div class="history-date">{log.created_at.strftime('%d/%m/%Y %H:%M')}</div>
                <div class="history-user">{log.user_id}</div>
                <div class="history-action">{log.action}</div>
                <div class="history-details">{log.details}</div>
            </div>
            '''
                        for log in logs
                    ]
                )
            }
            </div>
            <style>
            .history-list {{ max-width: 800px; margin: 1rem 0; }}
            .history-item {{
                border-left: 3px solid #3b82f6;
                padding: 1rem;
                margin-bottom: 1rem;
                background: #f9fafb;
            }}
            .history-date {{ font-size: 0.85rem; color: #6b7280; }}
            .history-user {{ font-weight: 600; color: #1f2937; }}
            .history-action {{ color: #3b82f6; font-weight: 500; }}
            .history-details {{ color: #4b5563; margin-top: 0.5rem; }}
            </style>
            """
        )


@router.post("/control/{control_id}/upload")
async def upload_evidence(
    request: Request,
    evaluation_id: str,
    control_id: str,
    csrf_token: str = Form(...),
    file: UploadFile = File(...),
):
    if not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    if file.size and file.size > 10 * 1024 * 1024:
        return HTMLResponse("Archivo demasiado grande (max 10MB)", status_code=400)

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)
        resp = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id,
                ControlResponse.control_id == control_id,
            )
        ).first()
        if not resp:
            raise HTTPException(status_code=404)

        upload_dir = Path(f"uploads/{evaluation_id}/{control_id}")
        upload_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file.filename).name.replace("..", "_")
        filepath = upload_dir / safe_name
        content = await file.read()
        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)
        file_size = len(content)
        content_hash = hashlib.sha256(content).hexdigest()
        ef = EvidenceFile(
            response_id=resp.id,
            filename=safe_name,
            filepath=str(filepath),
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            uploaded_by=user.id,
        )
        session.add(ef)
        session.add(
            AuditLog(
                user_id=user.id,
                action="EVIDENCE_UPLOADED",
                entity_type="evidence_file",
                entity_id=ef.id,
                details=f"Evidencia subida: {safe_name} ({file_size} bytes) para control {control_id}",
            )
        )
        session.commit()

    return RedirectResponse(
        url=f"/evaluate/{evaluation_id}/control/{control_id}", status_code=302
    )


@router.post("/control/{control_id}/delete-file/{file_id}")
async def delete_evidence(
    request: Request, evaluation_id: str, control_id: str, file_id: str
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")
    with Session(engine) as session:
        ef = session.get(EvidenceFile, file_id)
        if ef:
            ef_name = ef.filename
            path = Path(ef.filepath)
            if path.exists():
                path.unlink()
            session.add(
                AuditLog(
                    user_id=user.id,
                    action="EVIDENCE_DELETED",
                    entity_type="evidence_file",
                    entity_id=file_id,
                    details=f"Evidencia eliminada: {ef_name} del control {control_id}",
                )
            )
            session.delete(ef)
            session.commit()
    return RedirectResponse(
        url=f"/evaluate/{evaluation_id}/control/{control_id}", status_code=302
    )
