from fastapi import APIRouter, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session as SqlSession, select
from app.models import User, AuditLog
from app.auth import (
    get_current_user,
    create_session,
    delete_session,
    SESSION_COOKIE_NAME,
    SESSION_EXPIRE_HOURS,
    verify_password,
)
from app.templates_core import templates

router = APIRouter(prefix="", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user = get_current_user(session_id)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
):
    from app.database import engine

    with SqlSession(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()
        if not user or not verify_password(password, user.password_hash):
            session.add(
                AuditLog(
                    action="LOGIN_FAILED",
                    entity_type="auth",
                    details=f"Login fallido para: {email}",
                )
            )
            session.commit()
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Email o contrasena incorrectos"},
            )
        if not user.is_active:
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Usuario desactivado"}
            )

        db_session = create_session(user)
        session.add(
            AuditLog(
                user_id=user.id,
                action="LOGIN",
                entity_type="auth",
                details=f"Login exitoso: {email}",
            )
        )
        session.commit()
        resp = RedirectResponse(url="/dashboard", status_code=302)
        resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=db_session.id,
            httponly=True,
            samesite="lax",
            max_age=SESSION_EXPIRE_HOURS * 3600,
        )
        return resp


@router.post("/logout")
def logout(request: Request):
    from app.database import engine
    from app.models import Session as AppSession

    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if session_id:
        with SqlSession(engine) as db:
            app_session = db.exec(
                select(AppSession).where(AppSession.id == session_id)
            ).first()
            if app_session and app_session.user_id:
                db.add(
                    AuditLog(
                        user_id=app_session.user_id,
                        action="LOGOUT",
                        entity_type="auth",
                        details="Logout realizado",
                    )
                )
                db.commit()
        delete_session(session_id)
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp


@router.get("/logout")
def logout_get():
    return RedirectResponse(url="/login")
