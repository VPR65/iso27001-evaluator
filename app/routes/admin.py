from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from app.models import User, UserRole
from app.auth import get_current_user, require_role, hash_password
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
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

    resp = render(request, "admin/users.html", users=user_list)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@router.post("/all-users")
async def create_admin_user(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    email = form_data.get("email")
    name = form_data.get("name")
    password = form_data.get("password")

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
