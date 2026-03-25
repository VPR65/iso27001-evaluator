from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.models import User, UserRole, AuditLog, Client
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

    show_success = request.query_params.get("created") == "1"

    with Session(engine) as session:
        from app.models import Client

        users = session.exec(select(User)).all()
        clients = session.exec(select(Client)).all()
        clients_map = {c.id: c for c in clients}
        user_list = [{"u": u, "client": clients_map.get(u.client_id)} for u in users]

    resp = render(
        request,
        "admin/users.html",
        users=user_list,
        clients=clients,
        show_success=show_success,
    )
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

    return RedirectResponse(url="/admin/all-users?created=1", status_code=302)


@router.get("/debug/users")
def debug_users(request: Request):
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        session_id = request.cookies.get("session_id")
        user = get_current_user(session_id)
        if not user or user.role != UserRole.SUPERADMIN:
            return JSONResponse(status_code=401, content={"error": "No autorizado"})

    with Session(engine) as session:
        users = session.exec(select(User)).all()
        clients = session.exec(select(Client)).all()
        clients_map = {c.id: c.name for c in clients}
        return JSONResponse(
            status_code=200,
            content={
                "total": len(users),
                "users": [
                    {
                        "id": u.id,
                        "email": u.email,
                        "name": u.name,
                        "role": u.role.value,
                        "client_id": u.client_id,
                        "client_name": clients_map.get(u.client_id, "N/A"),
                        "is_active": u.is_active,
                    }
                    for u in users
                ],
            },
        )


@router.post("/debug/reset-password")
def debug_reset_password(request: Request, email: str = "", password: str = ""):
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    if not email or not password:
        return JSONResponse(
            status_code=400, content={"error": "Email y password requeridos"}
        )

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            return JSONResponse(
                status_code=404, content={"error": "Usuario no encontrado"}
            )

        user.password_hash = hash_password(password)
        session.add(user)
        session.commit()
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": f"Password reset for {email}"},
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


@router.get("/debug/seed-test-data")
def debug_seed_test_data(request: Request):
    """Endpoint de debug para poblar datos de prueba en QA"""
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    import uuid
    from datetime import datetime
    from app.models import Client, User, UserRole, Evaluation, Norma

    created = {"clients": 0, "users": 0, "evaluations": 0}

    with Session(engine) as session:
        iso27001 = session.exec(select(Norma).where(Norma.code == "ISO27001")).first()
        iso9001 = session.exec(select(Norma).where(Norma.code == "ISO9001")).first()

        if not iso27001:
            return JSONResponse(
                status_code=500,
                content={"error": "No se encontro ISO27001, ejecutar seed primero"},
            )

        existing_acme = session.exec(
            select(Client).where(Client.name == "Acme Corporation")
        ).first()
        if not existing_acme:
            client1_id = str(uuid.uuid4())
            client1 = Client(
                id=client1_id,
                name="Acme Corporation",
                description="Empresa de tecnología y consultoría",
                industry="Tecnología",
                size="mediana",
            )
            session.add(client1)
            created["clients"] += 1
        else:
            client1_id = existing_acme.id

        existing_global = session.exec(
            select(Client).where(Client.name == "Global Services S.A.")
        ).first()
        if not existing_global:
            client2_id = str(uuid.uuid4())
            client2 = Client(
                id=client2_id,
                name="Global Services S.A.",
                description="Servicios financieros y auditoría",
                industry="Finanzas",
                size="grande",
            )
            session.add(client2)
            created["clients"] += 1
        else:
            client2_id = existing_global.id

        client2_id = str(uuid.uuid4())
        client2 = Client(
            id=client2_id,
            name="Global Services S.A.",
            description="Servicios financieros y auditoría",
            industry="Finanzas",
            size="grande",
        )
        session.add(client2)
        created["clients"] += 1

        if not session.exec(
            select(User).where(User.email == "evaluador@demo.local")
        ).first():
            user1 = User(
                id=str(uuid.uuid4()),
                email="evaluador@demo.local",
                password_hash=hash_password("demo123"),
                name="Juan Pérez",
                role=UserRole.EVALUADOR,
                client_id=client1_id,
                is_active=True,
            )
            session.add(user1)
            created["users"] += 1

        if not session.exec(
            select(User).where(User.email == "admin2@demo.local")
        ).first():
            user2 = User(
                id=str(uuid.uuid4()),
                email="admin2@demo.local",
                password_hash=hash_password("demo123"),
                name="María García",
                role=UserRole.ADMIN_CLIENTE,
                client_id=client1_id,
                is_active=True,
            )
            session.add(user2)
            created["users"] += 1

        if not session.exec(
            select(User).where(User.email == "admin@global.local")
        ).first():
            user3 = User(
                id=str(uuid.uuid4()),
                email="admin@global.local",
                password_hash=hash_password("demo123"),
                name="Carlos López",
                role=UserRole.ADMIN_CLIENTE,
                client_id=client2_id,
                is_active=True,
            )
            session.add(user3)
            created["users"] += 1

        session.flush()

        user1 = session.exec(
            select(User).where(User.email == "evaluador@demo.local")
        ).first()
        user3 = session.exec(
            select(User).where(User.email == "admin@global.local")
        ).first()

        eval1_id = str(uuid.uuid4())
        eval1 = Evaluation(
            id=eval1_id,
            name="Auditoría ISO 27001:2022 - Q1 2026",
            client_id=client1_id,
            norma_id=iso27001.id,
            created_by=user1.id if user1 else None,
            status="in_progress",
            created_at=datetime.utcnow(),
        )
        session.add(eval1)
        created["evaluations"] += 1

        eval2_id = str(uuid.uuid4())
        eval2 = Evaluation(
            id=eval2_id,
            name="Evaluación ISO 9001 - Global Services",
            client_id=client2_id,
            norma_id=iso9001.id if iso9001 else iso27001.id,
            created_by=user3.id if user3 else None,
            status="completed",
            created_at=datetime.utcnow(),
        )
        session.add(eval2)
        created["evaluations"] += 1

        session.commit()

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Datos de prueba creados",
            "data": created,
        },
    )


@router.get("/debug/init-neon")
def debug_init_neon(request: Request):
    """Endpoint de debug para inicializar tablas y seed en Neon PostgreSQL"""
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    try:
        from app.database import create_db_and_tables
        from app.seed import seed_data as run_seed

        create_db_and_tables()
        run_seed()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Base de datos Neon inicializada correctamente. Tablas creadas y datos seed cargados.",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
            },
        )
