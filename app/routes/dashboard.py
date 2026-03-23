from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, func
from sqlalchemy import desc
from app.models import (
    User,
    Client,
    Evaluation,
    ControlResponse,
    ControlDefinition,
    Rfc,
    Sprint,
    UserRole,
)
from app.auth import get_current_user, SESSION_COOKIE_NAME
from app.database import engine
from app.templates_core import render

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            total_clients = session.exec(select(func.count(Client.id))).one()
            total_evals = session.exec(select(func.count(Evaluation.id))).one()
            total_rfcs = session.exec(select(func.count(Rfc.id))).one()
            active_sprints = session.exec(
                select(func.count(Sprint.id)).where(Sprint.status == "active")
            ).one()
            clients = session.exec(select(Client)).all()
        else:
            total_clients = session.exec(
                select(func.count(Client.id)).where(Client.id == user.client_id)
            ).one()
            total_evals = session.exec(
                select(func.count(Evaluation.id)).where(
                    Evaluation.client_id == user.client_id
                )
            ).one()
            total_rfcs = session.exec(
                select(func.count(Rfc.id)).where(Rfc.client_id == user.client_id)
            ).one()
            active_sprints = session.exec(
                select(func.count(Sprint.id)).where(
                    Sprint.client_id == user.client_id, Sprint.status == "active"
                )
            ).one()
            clients = [session.get(Client, user.client_id)] if user.client_id else []

        recent_evals = session.exec(
            select(Evaluation)
            .where(
                Evaluation.client_id == user.client_id
                if user.role != UserRole.SUPERADMIN
                else True
            )
            .order_by(desc(Evaluation.created_at))
            .limit(5)
        ).all()

        score = None
        if recent_evals:
            eval_id = recent_evals[0].id
            score = (
                session.exec(
                    select(func.avg(ControlResponse.maturity)).where(
                        ControlResponse.evaluation_id == eval_id
                    )
                ).one()
                or 0
            )

        return render(
            request,
            "dashboard/index.html",
            user,
            total_clients=total_clients,
            total_evals=total_evals,
            total_rfcs=total_rfcs,
            active_sprints=active_sprints,
            recent_evals=recent_evals,
            score=round(score, 2) if score else None,
            clients=clients,
        )
