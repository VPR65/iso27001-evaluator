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
from app.templates_core import render
from app.security import verify_csrf_token

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
            applicable = sum(1 for r in responses if not r.not_applicable)
            answered = sum(
                1 for r in responses if r.maturity > 0 and not r.not_applicable
            )
            na_count = sum(1 for r in responses if r.not_applicable)
            score = (
                round(
                    sum(r.maturity for r in responses if not r.not_applicable)
                    / applicable,
                    2,
                )
                if applicable
                else 0
            )
            pct = round(answered / applicable * 100, 1) if applicable else 0
            data.append(
                {
                    "eval": e,
                    "client": clients_map.get(e.client_id),
                    "score": score,
                    "progress": pct,
                    "answered": answered,
                    "total": applicable,
                    "na_count": na_count,
                }
            )

    return render(request, "evaluations/list.html", evaluations=data)


@router.get("/{evaluation_id}", response_class=HTMLResponse)
def view_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        evaluation = session.get(Evaluation, evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluacion no encontrada")
        if user.role != UserRole.SUPERADMIN and evaluation.client_id != user.client_id:
            raise HTTPException(
                status_code=403, detail="No tienes permiso para ver esta evaluacion"
            )

        client = (
            session.get(Client, evaluation.client_id) if evaluation.client_id else None
        )
        all_controls = session.exec(select(ControlDefinition)).all()
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id
            )
        ).all()
        resp_map = {r.control_id: r for r in responses}

        total = len(all_controls)
        applicable_total = sum(1 for r in responses if not r.not_applicable)
        na_count = sum(1 for r in responses if r.not_applicable)

        answered = sum(1 for r in responses if r.maturity > 0 and not r.not_applicable)
        progress = (
            int((answered / applicable_total) * 100) if applicable_total > 0 else 0
        )

        score_sum = sum(r.maturity for r in responses if not r.not_applicable)
        score = score_sum / applicable_total if applicable_total > 0 else 0

        domains = {}
        for ctrl in all_controls:
            domain = ctrl.domain
            if domain not in domains:
                domains[domain] = {
                    "controls": [],
                    "answered": 0,
                    "total": 0,
                    "na_count": 0,
                    "sum": 0,
                }
            resp = resp_map.get(ctrl.id)
            domains[domain]["controls"].append({"ctrl": ctrl, "response": resp})
            domains[domain]["total"] += 1
            if resp and resp.not_applicable:
                domains[domain]["na_count"] += 1
            elif resp and resp.maturity > 0:
                domains[domain]["answered"] += 1
                domains[domain]["sum"] += resp.maturity

        for domain, info in domains.items():
            applicable = info["total"] - info["na_count"]
            info["pct"] = (
                int((info["answered"] / applicable) * 100) if applicable > 0 else 0
            )
            info["avg"] = (
                round(info["sum"] / info["total"], 2) if info["total"] > 0 else 0
            )

    return render(
        request,
        "evaluations/detail.html",
        evaluation=evaluation,
        client=client,
        controls=all_controls,
        responses=resp_map,
        answered=answered,
        total=total,
        progress=progress,
        score=round(score, 2),
        domains=domains,
        user=user,
    )


@router.get("/new", response_class=HTMLResponse)
def new_evaluation_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    if user.role == UserRole.VISTA_SOLO:
        return RedirectResponse(url="/dashboard")
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    return render(
        request, "evaluations/form.html", clients=clients, evaluation=None, errors=None
    )


@router.post("/new")
async def create_evaluation(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    name = form_data.get("name")
    description = form_data.get("description", "")
    client_id = form_data.get("client_id")
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

        return render(
            request,
            "evaluations/detail.html",
            evaluation=evaluation,
            client=client,
            domains=domains,
            total=total,
            answered=answered,
            score=score,
            progress=progress,
        )


@router.post("/{evaluation_id}/start")
async def start_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

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
async def complete_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

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
async def delete_evaluation(request: Request, evaluation_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    from app.auth import require_role

    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

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
