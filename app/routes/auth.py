from fastapi import APIRouter, Request, Response, Form, HTTPException
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
from app.templates_core import render
from app.security import (
    check_rate_limit,
    record_failed_attempt,
    reset_rate_limit,
    verify_csrf_token,
)

router = APIRouter(prefix="", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Pagina de inicio de sesion.
    Muestra el formulario de login o redirige al dashboard si ya hay sesion activa.
    """
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user = get_current_user(session_id)
    if user:
        return RedirectResponse(url="/dashboard")

    return render(request, "login.html", error=None)


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Proceso de autenticacion de usuario.
    Verifica credenciales y crea sesion.
    Incluye proteccion rate limiting para prevenir ataques de fuerza bruta.
    """
    from app.database import engine

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return render(
            request,
            "login.html",
            error="Token de seguridad invalido. Refresca la pagina e intenta de nuevo.",
        )

    # Verificar rate limiting antes de procesar
    can_login, wait_time = check_rate_limit(email)
    if not can_login:
        return render(
            request,
            "login.html",
            error=f"Demasiados intentos. Espera {wait_time} segundos antes de intentar de nuevo.",
        )

    with SqlSession(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()

        if not user or not verify_password(password, user.password_hash):
            # Registrar intento fallido para rate limiting
            record_failed_attempt(email)

            # Registrar en audit log
            session.add(
                AuditLog(
                    action="LOGIN_FAILED",
                    entity_type="auth",
                    details=f"Login fallido para: {email}",
                )
            )
            session.commit()
            return render(
                request,
                "login.html",
                error="Email o contrasena incorrectos",
            )

        if not user.is_active:
            return render(
                request,
                "login.html",
                error="Usuario desactivado",
            )

        # Login exitoso - resetear rate limit
        reset_rate_limit(email)

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
async def logout(request: Request):
    from app.security import verify_csrf_token

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Token CSRF invalido")
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
