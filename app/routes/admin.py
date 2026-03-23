from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.models import User, UserRole, AuditLog
from app.auth import get_current_user, hash_password
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
from sqlmodel import Session, select

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/all-users", response_class=HTMLResponse)
def all_users(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != UserRole.SUPERADMIN:
        with Session(engine) as session:
            session.add(
                AuditLog(
                    user_id=user.id,
                    action="ACCESS_DENIED",
                    entity_type="admin",
                    details=f"Usuario {user.email} intento acceder a admin sin permisos",
                )
            )
            session.commit()
        return RedirectResponse(url="/dashboard")

    with Session(engine) as session:
        from app.models import Client

        users = session.exec(select(User)).all()
        clients = session.exec(select(Client)).all()
        clients_map = {c.id: c for c in clients}
        user_list = [{"u": u, "client": clients_map.get(u.client_id)} for u in users]

    resp = render(request, "admin/users.html", users=user_list, clients=clients)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@router.post("/all-users")
async def create_admin_user(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "No tienes permisos de superadmin"},
        )

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return JSONResponse(
            status_code=403, content={"success": False, "error": "Token CSRF invalido"}
        )

    email = form_data.get("email")
    name = form_data.get("name")
    password = form_data.get("password")
    role = form_data.get("role")
    client_id = form_data.get("client_id")

    if not email or not name or not password or not role or not client_id:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Faltan campos obligatorios"},
        )

    with Session(engine) as session:
        from app.models import Client

        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            return JSONResponse(
                status_code=409,
                content={"success": False, "error": "El usuario ya existe"},
            )
        client = session.get(Client, client_id)
        if not client:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Cliente no encontrado"},
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

        session.add(
            AuditLog(
                user_id=user.id,
                action="USER_CREATED",
                entity_type="user",
                entity_id=new_user.id,
                details=f"Usuario creado: {email} | Nombre: {name} | Rol: {role} | Cliente: {client.name}",
            )
        )
        session.commit()

    return JSONResponse(
        status_code=200,
        content={"success": True, "message": f"Usuario {email} creado exitosamente"},
    )


@router.get("/debug/users")
def debug_users(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(status_code=401, content={"error": "No autorizado"})

    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return JSONResponse(
            status_code=200,
            content={
                "total": len(users),
                "users": [
                    {"id": u.id, "email": u.email, "name": u.name, "role": u.role.value}
                    for u in users
                ],
            },
        )


@router.get("/debug/audit-logs")
def debug_audit_logs(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(status_code=401, content={"error": "No autorizado"})

    limit = int(request.query_params.get("limit", 50))
    with Session(engine) as session:
        from sqlalchemy import desc

        logs = session.exec(
            select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
        ).all()
        return JSONResponse(
            status_code=200,
            content={
                "total": len(logs),
                "logs": [
                    {
                        "id": l.id,
                        "action": l.action,
                        "entity_type": l.entity_type,
                        "entity_id": l.entity_id,
                        "user_id": l.user_id,
                        "details": l.details,
                        "ip_address": l.ip_address,
                        "created_at": str(l.created_at),
                    }
                    for l in logs
                ],
            },
        )
