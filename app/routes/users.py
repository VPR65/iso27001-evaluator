from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from app.models import User, Client, UserRole, AuditLog
from app.auth import get_current_user, require_role, hash_password
from app.database import engine
from app.templates_core import templates
from app.security import verify_csrf_token


def _log(session: Session, user_id: str, action: str, details: str = ""):
    session.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity_type="user",
            details=details,
        )
    )
    session.commit()


router = APIRouter(prefix="/clients/{client_id}/users", tags=["users"])


@router.get("", response_class=HTMLResponse)
def list_users(request: Request, client_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    with Session(engine) as session:
        if user.role == UserRole.ADMIN_CLIENTE and user.client_id != client_id:
            raise HTTPException(status_code=403)
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404)
        users = session.exec(select(User).where(User.client_id == client_id)).all()

    return templates.TemplateResponse(
        "users/list.html",
        {"request": request, "user": user, "client": client, "users": users},
    )


@router.get("/new", response_class=HTMLResponse)
def new_user_form(request: Request, client_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])
    return templates.TemplateResponse(
        "users/form.html",
        {
            "request": request,
            "user": user,
            "client_id": client_id,
            "edit_user": None,
            "roles": [r.value for r in UserRole if r != UserRole.SUPERADMIN],
            "errors": None,
        },
    )


@router.post("/new")
async def create_user(request: Request, client_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    email = form_data.get("email")
    name = form_data.get("name")
    role = form_data.get("role")
    password = form_data.get("password")

    with Session(engine) as session:
        if user.role == UserRole.ADMIN_CLIENTE and user.client_id != client_id:
            raise HTTPException(status_code=403)
        client = session.get(Client, client_id)
        if not client:
            _log(
                session,
                user.id,
                "USER_CREATE_FAILED",
                f"Cliente {client_id} no existe",
            )
            return templates.TemplateResponse(
                "users/form.html",
                {
                    "request": request,
                    "user": user,
                    "client_id": client_id,
                    "edit_user": None,
                    "roles": [r.value for r in UserRole if r != UserRole.SUPERADMIN],
                    "errors": {"client": "El cliente no existe. Crealo primero."},
                },
            )
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            _log(session, user.id, "USER_CREATE_FAILED", f"Email {email} ya existe")
            return templates.TemplateResponse(
                "users/form.html",
                {
                    "request": request,
                    "user": user,
                    "client_id": client_id,
                    "edit_user": None,
                    "roles": [r.value for r in UserRole if r != UserRole.SUPERADMIN],
                    "errors": {"email": "El email ya esta registrado"},
                },
            )
        new_user = User(
            email=email,
            name=name,
            role=UserRole(role),
            client_id=client_id,
            password_hash=hash_password(password),
        )
        session.add(new_user)
        session.commit()
        _log(session, user.id, "USER_CREATED", f"Creo usuario {email} con rol {role}")

    return RedirectResponse(url=f"/clients/{client_id}/users", status_code=302)


@router.post("/{user_id}/toggle")
async def toggle_user(request: Request, client_id: str, user_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    with Session(engine) as session:
        if user.role == UserRole.ADMIN_CLIENTE and user.client_id != client_id:
            raise HTTPException(status_code=403)
        edit_user = session.get(User, user_id)
        if edit_user and edit_user.client_id == client_id and edit_user.id != user.id:
            edit_user.is_active = not edit_user.is_active
            session.add(edit_user)
            session.commit()

    return RedirectResponse(url=f"/clients/{client_id}/users", status_code=302)
