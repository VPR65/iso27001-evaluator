from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from sqlalchemy import desc
from app.models import (
    Rfc,
    Client,
    User,
    UserRole,
    RfcStatus,
    RfcRiskLevel,
    RfcPriority,
    RfcImpact,
    RfcUrgency,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
import json

router = APIRouter(prefix="/rfcs", tags=["rfcs"])


def calc_priority(risk: str, impact: str, urgency: str) -> RfcPriority:
    score = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    total = score.get(risk, 1) + score.get(impact, 1) + score.get(urgency, 1)
    if total >= 9:
        return RfcPriority.P1
    elif total >= 7:
        return RfcPriority.P2
    elif total >= 4:
        return RfcPriority.P3
    return RfcPriority.P4


@router.get("", response_class=HTMLResponse)
def list_rfcs(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            rfcs_list = session.exec(select(Rfc).order_by(desc(Rfc.created_at))).all()
        else:
            rfcs_list = session.exec(
                select(Rfc)
                .where(Rfc.client_id == user.client_id)
                .order_by(Rfc.created_at.desc())
            ).all()
        rfc_data = []
        for r in rfcs_list:
            client = session.get(Client, r.client_id) if r.client_id else None
            rfc_data.append({"rfc": r, "client": client})

    return render(request, "rfcs/list.html", rfcs=rfc_data)


@router.get("/new", response_class=HTMLResponse)
def new_rfc_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    return render(request, "rfcs/form.html", clients=clients, rfc=None, errors=None)


@router.post("/new")
async def create_rfc(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    title = form_data.get("title")
    description = form_data.get("description")
    client_id = form_data.get("client_id")
    risk_level = form_data.get("risk_level")
    impact = form_data.get("impact")
    urgency = form_data.get("urgency")
    linked_controls = form_data.get("linked_controls", "[]")
    linked_documents = form_data.get("linked_documents", "[]")
    implementation_plan = form_data.get("implementation_plan", "")
    rollback_plan = form_data.get("rollback_plan", "")
    test_plan = form_data.get("test_plan", "")
    target_date = form_data.get("target_date", "")

    if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
        raise HTTPException(status_code=403)

    priority = calc_priority(risk_level, impact, urgency)
    target = None
    if target_date:
        try:
            from dateutil import parser

            target = parser.parse(target_date)
        except:
            target = None

    with Session(engine) as session:
        rfc = Rfc(
            title=title,
            description=description,
            client_id=client_id,
            applicant_id=user.id,
            risk_level=RfcRiskLevel(risk_level),
            impact=RfcImpact(impact),
            urgency=RfcUrgency(urgency),
            priority=priority,
            linked_controls=linked_controls,
            linked_documents=linked_documents,
            implementation_plan=implementation_plan,
            rollback_plan=rollback_plan,
            test_plan=test_plan,
            target_date=target,
        )
        session.add(rfc)
        session.commit()

    return RedirectResponse(url="/rfcs", status_code=302)


@router.get("/{rfc_id}", response_class=HTMLResponse)
def view_rfc(request: Request, rfc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        rfc = session.get(Rfc, rfc_id)
        if not rfc or (
            user.role != UserRole.SUPERADMIN and rfc.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        client = session.get(Client, rfc.client_id) if rfc.client_id else None
        linked_controls = json.loads(rfc.linked_controls) if rfc.linked_controls else []
        linked_docs = json.loads(rfc.linked_documents) if rfc.linked_documents else []

    return render(
        request,
        "rfcs/detail.html",
        rfc=rfc,
        client=client,
        linked_controls=linked_controls,
        linked_docs=linked_docs,
    )


@router.post("/{rfc_id}/status")
async def update_rfc_status(request: Request, rfc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    status = form_data.get("status")
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])
    from datetime import datetime

    with Session(engine) as session:
        rfc = session.get(Rfc, rfc_id)
        if not rfc or (
            user.role != UserRole.SUPERADMIN and rfc.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        rfc.status = RfcStatus(status)
        if status == "implemented":
            rfc.completed_at = datetime.utcnow()
        if status == "evaluated":
            rfc.evaluator_id = user.id
        if status == "approved":
            rfc.approver_id = user.id
        session.add(rfc)
        session.commit()
    return RedirectResponse(url=f"/rfcs/{rfc_id}", status_code=302)
