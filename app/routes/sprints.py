from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from sqlalchemy import desc
from app.models import (
    Sprint,
    BacklogItem,
    SprintTask,
    Client,
    User,
    UserRole,
    TaskStatus,
    SprintStatus,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.templates_core import templates

router = APIRouter(prefix="/sprints", tags=["sprints"])


@router.get("", response_class=HTMLResponse)
def list_sprints(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            sprints_list = session.exec(
                select(Sprint).order_by(Sprint.created_at.desc())
            ).all()
        else:
            sprints_list = session.exec(
                select(Sprint)
                .where(Sprint.client_id == user.client_id)
                .order_by(Sprint.created_at.desc())
            ).all()

        sprint_data = []
        for s in sprints_list:
            items = session.exec(
                select(BacklogItem).where(BacklogItem.sprint_id == s.id)
            ).all()
            done = sum(1 for i in items if i.status == TaskStatus.DONE)
            sprint_data.append(
                {"sprint": s, "total_items": len(items), "done_items": done}
            )

    return templates.TemplateResponse(
        "sprints/list.html", {"request": request, "user": user, "sprints": sprint_data}
    )


@router.get("/new", response_class=HTMLResponse)
def new_sprint_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    return templates.TemplateResponse(
        "sprints/form.html",
        {"request": request, "user": user, "clients": clients, "sprint": None},
    )


@router.post("/new")
def create_sprint(
    request: Request,
    name: str = Form(...),
    goal: str = Form(""),
    client_id: str = Form(...),
    start_date: str = Form(""),
    end_date: str = Form(""),
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
        raise HTTPException(status_code=403)

    start = end = None
    if start_date:
        try:
            from dateutil import parser

            start = parser.parse(start_date)
            end = parser.parse(end_date) if end_date else None
        except:
            pass

    with Session(engine) as session:
        sprint = Sprint(
            name=name,
            goal=goal,
            client_id=client_id,
            created_by=user.id,
            start_date=start,
            end_date=end,
        )
        session.add(sprint)
        session.commit()

    return RedirectResponse(url="/sprints", status_code=302)


@router.get("/{sprint_id}", response_class=HTMLResponse)
def view_sprint(request: Request, sprint_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        sprint = session.get(Sprint, sprint_id)
        if not sprint or (
            user.role != UserRole.SUPERADMIN and sprint.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        items = session.exec(
            select(BacklogItem).where(BacklogItem.sprint_id == sprint_id)
        ).all()
        backlog_items = []
        for item in items:
            tasks = session.exec(
                select(SprintTask).where(SprintTask.backlog_item_id == item.id)
            ).all()
            backlog_items.append({"item": item, "tasks": tasks})

    return templates.TemplateResponse(
        "sprints/detail.html",
        {"request": request, "user": user, "sprint": sprint, "items": backlog_items},
    )


@router.post("/{sprint_id}/add-item")
def add_backlog_item(
    request: Request,
    sprint_id: str,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium"),
    effort_hours: int = Form(0),
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    with Session(engine) as session:
        sprint = session.get(Sprint, sprint_id)
        if not sprint or (
            user.role != UserRole.SUPERADMIN and sprint.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        item = BacklogItem(
            sprint_id=sprint_id,
            title=title,
            description=description,
            priority=priority,
            effort_hours=effort_hours,
            client_id=sprint.client_id,
            created_by=user.id,
        )
        session.add(item)
        session.commit()
    return RedirectResponse(url=f"/sprints/{sprint_id}", status_code=302)


@router.post("/{sprint_id}/status")
def update_sprint_status(request: Request, sprint_id: str, status: str = Form(...)):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    with Session(engine) as session:
        sprint = session.get(Sprint, sprint_id)
        if sprint:
            sprint.status = SprintStatus(status)
            session.add(sprint)
            session.commit()
    return RedirectResponse(url=f"/sprints/{sprint_id}", status_code=302)
