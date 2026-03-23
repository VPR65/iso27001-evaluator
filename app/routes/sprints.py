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
from app.templates_core import render
from app.security import verify_csrf_token

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

    return render(request, "sprints/list.html", sprints=sprint_data)


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
    return render(request, "sprints/form.html", clients=clients, sprint=None)


@router.post("/new")
async def create_sprint(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    name = form_data.get("name")
    goal = form_data.get("goal", "")
    client_id = form_data.get("client_id")
    start_date = form_data.get("start_date", "")
    end_date = form_data.get("end_date", "")

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

    return render(request, "sprints/detail.html", sprint=sprint, items=backlog_items)


@router.post("/{sprint_id}/add-item")
async def add_backlog_item(request: Request, sprint_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    title = form_data.get("title")
    description = form_data.get("description", "")
    priority = form_data.get("priority", "medium")
    effort_hours = int(form_data.get("effort_hours", 0) or 0)

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
async def update_sprint_status(request: Request, sprint_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    status = form_data.get("status")
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
