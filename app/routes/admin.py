from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models import User, UserRole
from app.auth import get_current_user, require_role, hash_password
from app.database import engine
from app.templates_core import templates
from sqlmodel import Session, select

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/all-users", response_class=HTMLResponse)
def all_users(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    with Session(engine) as session:
        from app.models import Client

        users = session.exec(select(User)).all()
        clients = session.exec(select(Client)).all()
        clients_map = {c.id: c for c in clients}
        user_list = [{"u": u, "client": clients_map.get(u.client_id)} for u in users]

    return templates.TemplateResponse(
        "admin/users.html", {"request": request, "user": user, "users": user_list}
    )


@router.post("/all-users")
def create_admin_user(
    request: Request,
    email: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            return RedirectResponse(url="/admin/all-users", status_code=302)
        new_user = User(
            email=email,
            name=name,
            role=UserRole.ADMIN_CLIENTE,
            password_hash=hash_password(password),
        )
        session.add(new_user)
        session.commit()

    return RedirectResponse(url="/admin/all-users", status_code=302)
