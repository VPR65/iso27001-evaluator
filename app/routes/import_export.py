from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlmodel import Session, select
from app.models import (
    Evaluation,
    Client,
    ControlDefinition,
    ControlResponse,
    User,
    UserRole,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.security import verify_csrf_token
import pandas as pd
from datetime import datetime
from io import BytesIO

router = APIRouter(prefix="/import-export", tags=["import_export"])


@router.get("/export/{evaluation_id}")
def export_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401)

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)

        all_controls = session.exec(
            select(ControlDefinition).order_by(ControlDefinition.code)
        ).all()
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id
            )
        ).all()
        resp_map = {r.control_id: r for r in responses}

        data = []
        for ctrl in all_controls:
            r = resp_map.get(ctrl.id)
            data.append(
                {
                    "Codigo": ctrl.code,
                    "Dominio": ctrl.domain,
                    "Titulo": ctrl.title,
                    "Descripcion": ctrl.description,
                    "Madurez": r.maturity if r else 0,
                    "Notas": r.notes if r else "",
                    "Fecha Actualizacion": r.updated_at.strftime("%Y-%m-%d %H:%M")
                    if r and r.updated_at
                    else "",
                }
            )

        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Evaluacion", index=False)
        output.seek(0)

        filename = (
            f"evaluacion_{evaluation.name}_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
        )
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )


@router.get("/import", response_class=HTMLResponse)
def import_page(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    from app.templates_core import templates

    return templates.TemplateResponse(
        "import_export/import.html",
        {"request": request, "user": user, "clients": clients},
    )


@router.post("/import")
async def import_excel(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    client_id = form_data.get("client_id")
    name = form_data.get("name")
    evaluation_id = form_data.get("evaluation_id")
    file = form_data.get("file")

    if not file.filename.endswith((".xlsx", ".xls")):
        return HTMLResponse(
            "Solo se permiten archivos Excel (.xlsx, .xls)", status_code=400
        )

    content = await file.read()
    try:
        df = pd.read_excel(BytesIO(content))
    except Exception as e:
        return HTMLResponse(f"Error al leer Excel: {e}", status_code=400)

    with Session(engine) as session:
        if evaluation_id:
            eval_obj = session.get(Evaluation, evaluation_id)
        else:
            if not name or not client_id:
                return HTMLResponse("Faltan campos obligatorios", status_code=400)
            if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
                raise HTTPException(status_code=403)
            eval_obj = Evaluation(name=name, client_id=client_id, created_by=user.id)
            session.add(eval_obj)
            session.commit()
            session.refresh(eval_obj)
            all_controls = session.exec(select(ControlDefinition)).all()
            for ctrl in all_controls:
                resp = ControlResponse(
                    evaluation_id=eval_obj.id,
                    control_id=ctrl.id,
                    maturity=0,
                    created_by=user.id,
                )
                session.add(resp)
            session.commit()

        ctrl_map = {c.code: c for c in session.exec(select(ControlDefinition)).all()}
        responses = session.exec(
            select(ControlResponse).where(ControlResponse.evaluation_id == eval_obj.id)
        ).all()
        resp_map = {r.control_id: r for r in responses}

        for _, row in df.iterrows():
            code = str(row.get("Codigo", "")).strip()
            maturity = row.get("Madurez")
            notes = str(row.get("Notas", ""))
            if code in ctrl_map and pd.notna(maturity):
                ctrl = ctrl_map[code]
                r = resp_map.get(ctrl.id)
                if r:
                    r.maturity = int(maturity) if pd.notna(maturity) else 0
                    r.notes = notes if notes != "nan" else ""
                    session.add(r)
        session.commit()

    return RedirectResponse(url=f"/evaluations/{eval_obj.id}", status_code=302)
