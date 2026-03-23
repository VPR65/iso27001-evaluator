from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlmodel import Session, select, func
from app.models import Evaluation, ControlResponse, ControlDefinition, User, UserRole
from app.auth import get_current_user
from app.database import engine
from app.templates_core import templates

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/{evaluation_id}", response_class=HTMLResponse)
def stats_page(request: Request, evaluation_id: str):
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

        all_controls = session.exec(select(ControlDefinition)).all()
        ctrl_map = {c.id: c for c in all_controls}
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id
            )
        ).all()
        resp_map = {r.control_id: r for r in responses}

        domains = {}
        for ctrl in all_controls:
            domain = ctrl.domain
            if domain not in domains:
                domains[domain] = {
                    "score": 0,
                    "count": 0,
                    "critical": 0,
                    "controls": [],
                }
            r = resp_map.get(ctrl.id)
            if r:
                domains[domain]["score"] += r.maturity
                domains[domain]["count"] += 1
                if r.maturity < 2:
                    domains[domain]["critical"] += 1
                domains[domain]["controls"].append(
                    {"ctrl": ctrl, "maturity": r.maturity, "notes": r.notes}
                )
            else:
                domains[domain]["controls"].append(
                    {"ctrl": ctrl, "maturity": 0, "notes": ""}
                )

        domain_data = []
        for d, info in domains.items():
            avg = round(info["score"] / info["count"], 2) if info["count"] else 0
            domain_data.append(
                {
                    "name": d,
                    "avg": avg,
                    "count": info["count"],
                    "critical": info["critical"],
                }
            )
        domain_data.sort(key=lambda x: x["avg"])

        score = (
            round(sum(r.maturity for r in responses) / len(responses), 2)
            if responses
            else 0
        )
        critical = sum(1 for r in responses if r.maturity < 2)
        radar = [
            {
                "domain": d,
                "avg": round(info["score"] / info["count"], 2) if info["count"] else 0,
            }
            for d, info in domains.items()
        ]
        critical_controls = [
            {"ctrl": ctrl_map.get(r.control_id), "maturity": r.maturity}
            for r in responses
            if r.maturity < 2
        ]
        critical_controls = [c for c in critical_controls if c["ctrl"]]

        return templates.TemplateResponse(
            "stats/report.html",
            {
                "request": request,
                "user": user,
                "evaluation": evaluation,
                "domain_data": domain_data,
                "score": score,
                "answered": len(responses),
                "total": len(all_controls),
                "critical": critical,
                "radar": radar,
                "critical_controls": critical_controls,
            },
        )


@router.get("/{evaluation_id}/json")
def stats_json(request: Request, evaluation_id: str):
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

        all_controls = session.exec(select(ControlDefinition)).all()
        responses = session.exec(
            select(ControlResponse).where(
                ControlResponse.evaluation_id == evaluation_id
            )
        ).all()
        resp_map = {r.control_id: r for r in responses}
        domains = {}
        for ctrl in all_controls:
            domain = ctrl.domain
            if domain not in domains:
                domains[domain] = {"score": 0, "count": 0}
            r = resp_map.get(ctrl.id)
            if r:
                domains[domain]["score"] += r.maturity
                domains[domain]["count"] += 1

        radar = {
            d: round(info["score"] / info["count"], 2) if info["count"] else 0
            for d, info in domains.items()
        }
        score = (
            round(sum(r.maturity for r in responses) / len(responses), 2)
            if responses
            else 0
        )
        return JSONResponse(
            {
                "evaluation_id": evaluation_id,
                "score": score,
                "answered": len(responses),
                "total": len(all_controls),
                "domains": radar,
            }
        )
