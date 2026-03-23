from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, func
from sqlalchemy import desc
from app.models import (
    Evaluation,
    Client,
    ControlDefinition,
    ControlResponse,
    User,
    UserRole,
    EvaluationStatus,
    AuditLog,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.templates_core import templates

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_class=HTMLResponse)
def list_evaluations(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            evals = session.exec(
                select(Evaluation).order_by(desc(Evaluation.created_at))
            ).all()
            clients_map = {}
            for e in evals:
                if e.client_id not in clients_map:
                    clients_map[e.client_id] = session.get(Client, e.client_id)
        else:
            evals = session.exec(
                select(Evaluation)
                .where(Evaluation.client_id == user.client_id)
                .order_by(desc(Evaluation.created_at))
            ).all()
            clients_map = {user.client_id: session.get(Client, user.client_id)}

        data = []
        for e in evals:
            responses = session.exec(
                select(ControlResponse).where(ControlResponse.evaluation_id == e.id)
            ).all()
            total_controls = session.exec(
                select(func.count(ControlDefinition.id))
            ).one()
            answered = len(responses)
            score = (
                round(sum(r.maturity for r in responses) / answered, 2)
                if answered
                else 0
            )
            pct = round(answered / total_controls * 100, 1) if total_controls else 0
            data.append(
                {
                    "eval": e,
                    "client": clients_map.get(e.client_id),
                    "score": score,
                    "progress": pct,
                    "answered": answered,
                    "total": total_controls,
                }
            )

    return templates.TemplateResponse(
        "evaluations/list.html", {"request": request, "user": user, "evaluations": data}
    )


@router.get("/new", response_class=HTMLResponse)
def new_evaluation_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    return templates.TemplateResponse(
        "evaluations/form.html",
        {
            "request": request,
            "user": user,
            "clients": clients,
            "evaluation": None,
            "errors": None,
        },
    )


@router.post("/new")
def create_evaluation(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    client_id: str = Form(...),
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
            raise HTTPException(status_code=403)
        evaluation = Evaluation(
            name=name,
            description=description,
            client_id=client_id,
            created_by=user.id,
            status=EvaluationStatus.DRAFT,
        )
        session.add(evaluation)
        session.commit()
        session.refresh(evaluation)
        all_controls = session.exec(select(ControlDefinition)).all()
        for ctrl in all_controls:
            resp = ControlResponse(
                evaluation_id=evaluation.id,
                control_id=ctrl.id,
                maturity=0,
                created_by=user.id,
            )
            session.add(resp)
        session.commit()
        session.add(
            AuditLog(
                user_id=user.id,
                action="EVALUATION_CREATED",
                entity_type="evaluation",
                entity_id=evaluation.id,
                details=f"Evaluacion creada: {name} (ID: {evaluation.id})",
            )
        )
        session.commit()
    return RedirectResponse(url=f"/evaluations/{evaluation.id}", status_code=302)


def view_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404)
        if user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id:
            raise HTTPException(status_code=403)
        client = session.get(Client, evaluation.client_id)
        all_controls = session.exec(select(ControlDefinition)).all()
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id
            )
        ).all()
        resp_map = {r.control_id: r for r in responses}

        domains = {}
        for ctrl in all_controls:
            r = resp_map.get(ctrl.id)
            domain = ctrl.domain
            if domain not in domains:
                domains[domain] = {
                    "controls": [],
                    "total": 0,
                    "count": 0,
                    "answered": 0,
                }
            domains[domain]["controls"].append({"ctrl": ctrl, "response": r})
            domains[domain]["total"] += 1
            if r and r.maturity > 0:
                domains[domain]["answered"] += 1
            if r:
                domains[domain]["count"] += r.maturity

        for d in domains:
            cnt = sum(1 for c in domains[d]["controls"] if resp_map.get(c["ctrl"].id))
            domains[d]["avg"] = round(domains[d]["count"] / cnt, 2) if cnt else 0
            domains[d]["pct"] = (
                round(domains[d]["answered"] / domains[d]["total"] * 100, 1)
                if domains[d]["total"]
                else 0
            )

        total = len(all_controls)
        answered = sum(1 for r in responses if r.maturity > 0)
        score = (
            round(sum(r.maturity for r in responses) / answered, 2) if answered else 0
        )
        progress = round(answered / total * 100, 1) if total else 0

        return templates.TemplateResponse(
            "evaluations/detail.html",
            {
                "request": request,
                "user": user,
                "evaluation": evaluation,
                "client": client,
                "domains": domains,
                "total": total,
                "answered": answered,
                "score": score,
                "progress": progress,
            },
        )


@router.post("/{evaluation_id}/start")
def start_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation or (
            user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id
        ):
            raise HTTPException(status_code=403)
        evaluation.status = EvaluationStatus.IN_PROGRESS
        session.add(evaluation)
        session.add(
            AuditLog(
                user_id=user.id,
                action="EVALUATION_STARTED",
                entity_type="evaluation",
                entity_id=evaluation_id,
                details=f"Evaluacion iniciada: {evaluation.name}",
            )
        )
        session.commit()
    return RedirectResponse(url=f"/evaluations/{evaluation_id}", status_code=302)


@router.post("/{evaluation_id}/complete")
def complete_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])
    from datetime import datetime

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404)
        evaluation.status = EvaluationStatus.COMPLETED
        evaluation.completed_at = datetime.utcnow()
        session.add(evaluation)
        session.add(
            AuditLog(
                user_id=user.id,
                action="EVALUATION_COMPLETED",
                entity_type="evaluation",
                entity_id=evaluation_id,
                details=f"Evaluacion completada: {evaluation.name}",
            )
        )
        session.commit()
    return RedirectResponse(url=f"/evaluations/{evaluation_id}", status_code=302)


@router.post("/{evaluation_id}/delete")
def delete_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])
    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if evaluation and (
            user.role == UserRole.SUPERADMIN or evaluation.client_id == user.client_id
        ):
            eval_name = evaluation.name
            session.delete(evaluation)
            session.add(
                AuditLog(
                    user_id=user.id,
                    action="EVALUATION_DELETED",
                    entity_type="evaluation",
                    entity_id=evaluation_id,
                    details=f"Evaluacion eliminada: {eval_name}",
                )
            )
            session.commit()
    return RedirectResponse(url="/evaluations", status_code=302)
