from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select, func
from app.models import Client, User, UserRole, AuditLog
from app.auth import get_current_user, require_role
from app.database import engine
from app.templates_core import templates, render
from app.security import verify_csrf_token

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_class=HTMLResponse)
def list_clients(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    with Session(engine) as session:
        clients = session.exec(select(Client)).all()
        counts = {}
        for c in clients:
            cnt = session.exec(
                select(func.count(User.id)).where(User.client_id == c.id)
            ).one()
            counts[c.id] = cnt

    return render(request, "clients/list.html", clients=clients, counts=counts)


@router.get("/new", response_class=HTMLResponse)
def new_client_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])
    return render(request, "clients/form.html", client=None, errors=None)


@router.post("/new")
async def create_client(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    name = form_data.get("name")
    sector = form_data.get("sector", "")

    with Session(engine) as session:
        client = Client(name=name, sector=sector)
        session.add(client)
        session.commit()
        session.refresh(client)
        log = AuditLog(
            user_id=user.id,
            client_id=client.id,
            action="create",
            entity_type="client",
            entity_id=client.id,
            details=f"Cliente creado: {name}",
        )
        session.add(log)
        session.commit()

    return RedirectResponse(url="/clients", status_code=302)


@router.post("/{client_id}/delete")
async def delete_client(request: Request, client_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    with Session(engine) as session:
        client = session.get(Client, client_id)
        if client:
            session.delete(client)
            session.commit()

    return RedirectResponse(url="/clients", status_code=302)
