from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.models import User, UserRole, AuditLog, Client
from app.auth import get_current_user, hash_password
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
from sqlmodel import Session, select, func, desc

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/clients", response_class=HTMLResponse)
def manage_clients(request: Request):
    """Panel de administracion de clientes"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != UserRole.SUPERADMIN:
        return RedirectResponse(url="/dashboard")

    show_success = request.query_params.get("created") == "1"
    show_deleted = request.query_params.get("deleted") == "1"

    with Session(engine) as session:
        from app.models import Evaluation, User

        clients = session.exec(select(Client)).all()
        clients_data = []

        for client in clients:
            eval_count = session.exec(
                select(func.count(Evaluation.id)).where(
                    Evaluation.client_id == client.id
                )
            ).one()
            user_count = session.exec(
                select(func.count(User.id)).where(User.client_id == client.id)
            ).one()
            clients_data.append(
                {
                    "client": client,
                    "eval_count": eval_count,
                    "user_count": user_count,
                }
            )

    return render(
        request,
        "admin/clients.html",
        clients_data=clients_data,
        show_success=show_success,
        show_deleted=show_deleted,
    )


@router.post("/clients")
async def create_client(request: Request):
    """Crear nuevo cliente"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "No tienes permisos"},
        )

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return JSONResponse(
            status_code=403, content={"success": False, "error": "Token CSRF invalido"}
        )

    name = form_data.get("name")
    description = form_data.get("description", "")
    industry = form_data.get("industry", "")
    size = form_data.get("size", "mediana")
    sector = form_data.get("sector", "")

    if not name or not name.strip():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "El nombre es requerido"},
        )

    with Session(engine) as session:
        client = Client(
            name=name,
            description=description,
            industry=industry,
            size=size,
            sector=sector,
        )
        session.add(client)
        session.add(
            AuditLog(
                user_id=user.id,
                action="CLIENT_CREATED",
                entity_type="client",
                entity_id=client.id,
                details=f"Cliente creado: {name}",
            )
        )
        session.commit()

    return RedirectResponse(url="/admin/clients?created=1", status_code=302)


@router.post("/clients/{client_id}/delete")
async def delete_client(request: Request, client_id: str):
    """Eliminar cliente con confirmacion de password"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "No tienes permisos"},
        )

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return JSONResponse(
            status_code=403, content={"success": False, "error": "Token CSRF invalido"}
        )

    confirm_password = form_data.get("confirm_password", "")
    if not confirm_password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Debe confirmar con su password"},
        )

    from app.auth import verify_password

    if not verify_password(confirm_password, user.password_hash):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Password incorrecto"},
        )

    with Session(engine) as session:
        from app.models import Evaluation, ControlResponse, User, Session as UserSession

        client = session.get(Client, client_id)
        if not client:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Cliente no encontrado"},
            )

        client_name = client.name

        evals = session.exec(
            select(Evaluation).where(Evaluation.client_id == client_id)
        ).all()

        for eval_obj in evals:
            session.exec(
                select(ControlResponse).where(
                    ControlResponse.evaluation_id == eval_obj.id
                )
            )
            session.query(ControlResponse).where(
                ControlResponse.evaluation_id == eval_obj.id
            ).delete()
            session.delete(eval_obj)

        session.query(User).where(User.client_id == client_id).delete()
        session.query(UserSession).where(
            UserSession.user_id.in_(
                session.exec(select(User.id).where(User.client_id == client_id))
            )
        ).delete(synchronize_session=False)

        session.delete(client)

        session.add(
            AuditLog(
                user_id=user.id,
                action="CLIENT_DELETED",
                entity_type="client",
                entity_id=client_id,
                details=f"Cliente eliminado: {client_name}",
            )
        )
        session.commit()

    return RedirectResponse(url="/admin/clients?deleted=1", status_code=302)


@router.get("/evaluations", response_class=HTMLResponse)
def manage_evaluations(request: Request):
    """Panel de administracion de evaluaciones"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != UserRole.SUPERADMIN:
        return RedirectResponse(url="/dashboard")

    show_deleted = request.query_params.get("deleted") == "1"

    with Session(engine) as session:
        from app.models import (
            Evaluation,
            Client,
            Norma,
            ControlResponse,
            ControlDefinition,
        )

        evaluations = session.exec(
            select(Evaluation).order_by(desc(Evaluation.created_at))
        ).all()

        evals_data = []
        for eval_obj in evaluations:
            client = (
                session.get(Client, eval_obj.client_id) if eval_obj.client_id else None
            )
            norma = session.get(Norma, eval_obj.norma_id) if eval_obj.norma_id else None

            response_count = session.exec(
                select(func.count(ControlResponse.id)).where(
                    ControlResponse.evaluation_id == eval_obj.id
                )
            ).one()

            total_controls = 0
            progress_percent = 0
            if norma:
                total_controls = session.exec(
                    select(func.count(ControlDefinition.id)).where(
                        ControlDefinition.norma_id == norma.id
                    )
                ).one()
                if total_controls > 0:
                    progress_percent = min(
                        100, round((response_count / total_controls) * 100, 1)
                    )

            evals_data.append(
                {
                    "evaluation": eval_obj,
                    "client": client,
                    "norma": norma,
                    "response_count": response_count,
                    "total_controls": total_controls,
                    "progress_percent": progress_percent,
                }
            )

    return render(
        request,
        "admin/evaluations.html",
        evaluations=evals_data,
        show_deleted=show_deleted,
    )


@router.post("/evaluations/{eval_id}/delete")
async def delete_evaluation(request: Request, eval_id: str):
    """Eliminar evaluacion con confirmacion de password"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "No tienes permisos"},
        )

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return JSONResponse(
            status_code=403, content={"success": False, "error": "Token CSRF invalido"}
        )

    confirm_password = form_data.get("confirm_password", "")
    if not confirm_password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Debe confirmar con su password"},
        )

    from app.auth import verify_password

    if not verify_password(confirm_password, user.password_hash):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Password incorrecto"},
        )

    with Session(engine) as session:
        from app.models import ControlResponse

        evaluation = session.get(Evaluation, eval_id)
        if not evaluation:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Evaluacion no encontrada"},
            )

        eval_name = evaluation.name

        session.query(ControlResponse).where(
            ControlResponse.evaluation_id == eval_id
        ).delete(synchronize_session=False)
        session.delete(evaluation)

        session.add(
            AuditLog(
                user_id=user.id,
                action="EVALUATION_DELETED",
                entity_type="evaluation",
                entity_id=eval_id,
                details=f"Evaluacion eliminada: {eval_name}",
            )
        )
        session.commit()

    return RedirectResponse(url="/admin/evaluations?deleted=1", status_code=302)


@router.post("/users/{user_id}/delete")
async def delete_user(request: Request, user_id: str):
    """Eliminar usuario con confirmacion de password"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user or user.role != UserRole.SUPERADMIN:
        return JSONResponse(
            status_code=401,
            content={"success": False, "error": "No tienes permisos"},
        )

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        return JSONResponse(
            status_code=403, content={"success": False, "error": "Token CSRF invalido"}
        )

    confirm_password = form_data.get("confirm_password", "")
    if not confirm_password:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Debe confirmar con su password"},
        )

    from app.auth import verify_password

    if not verify_password(confirm_password, user.password_hash):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Password incorrecto"},
        )

    with Session(engine) as session:
        from app.models import Session as UserSession

        target_user = session.get(User, user_id)
        if not target_user:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Usuario no encontrado"},
            )

        if target_user.email == "admin@iso27001.local":
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "No se puede eliminar el superadmin",
                },
            )

        user_email = target_user.email
        user_name = target_user.name

        session.query(UserSession).where(UserSession.user_id == user_id).delete(
            synchronize_session=False
        )
        session.delete(target_user)

        session.add(
            AuditLog(
                user_id=user.id,
                action="USER_DELETED",
                entity_type="user",
                entity_id=user_id,
                details=f"Usuario eliminado: {user_email} ({user_name})",
            )
        )
        session.commit()

    return RedirectResponse(url="/admin/all-users?deleted=1", status_code=302)


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
    show_deleted = request.query_params.get("deleted") == "1"

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
        show_deleted=show_deleted,
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


@router.get("/debug/clear-evaluations")
def debug_clear_evaluations(request: Request):
    """Endpoint de debug para eliminar todas las evaluaciones de prueba"""
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    try:
        from app.models import ControlResponse, Evaluation

        deleted_responses = 0
        deleted_evals = 0

        with Session(engine) as session:
            # Contar antes de borrar
            responses = session.exec(select(ControlResponse)).all()
            evals = session.exec(select(Evaluation)).all()
            deleted_responses = len(responses)
            deleted_evals = len(evals)

            # Borrar en orden (primero responses por FK)
            session.exec(select(ControlResponse).where(ControlResponse.id != None))
            session.query(ControlResponse).delete()
            session.query(Evaluation).delete()
            session.commit()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Eliminadas {deleted_evals} evaluaciones y {deleted_responses} respuestas de control",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.get("/debug/clear-test-data")
def debug_clear_test_data(request: Request):
    """Endpoint de debug para eliminar TODOS los datos de prueba (evaluaciones, usuarios demo, clientes demo)"""
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    try:
        from app.models import ControlResponse, Evaluation, User, Client

        with Session(engine) as session:
            # Contar
            deleted = {
                "evaluations": session.query(Evaluation).count(),
                "control_responses": session.query(ControlResponse).count(),
                "test_users": 0,
                "test_clients": 0,
            }

            # Usuarios de prueba (no superadmin, no admin@iso27001)
            test_users = session.exec(
                select(User).where(User.email.notin_(["admin@iso27001.local"]))
            ).all()
            deleted["test_users"] = len(test_users)

            # Clientes de prueba (no Cliente Demo)
            test_clients = session.exec(
                select(Client).where(Client.name.notin_(["Cliente Demo"]))
            ).all()
            deleted["test_clients"] = len(test_clients)

            # Borrar en orden (primero responses, luego evals, luego users, luego clients)
            session.query(ControlResponse).delete()
            session.query(Evaluation).delete()
            for u in test_users:
                session.delete(u)
            for c in test_clients:
                session.delete(c)
            session.commit()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Datos de prueba eliminados",
                "deleted": deleted,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.get("/debug/reset-all")
def debug_reset_all(request: Request):
    """Endpoint de debug para RESETEAR toda la base de datos (elimina TODO y recrea seed)"""
    debug_token = request.query_params.get("token")
    if debug_token != "qa-debug-2024":
        return JSONResponse(status_code=403, content={"error": "Token invalido"})

    try:
        from app.models import (
            AuditLog,
            SprintTask,
            Sprint,
            RFC,
            DocumentVersion,
            Document,
            ControlResponse,
            EvidenceFile,
            Evaluation,
            User,
            Client,
        )
        from app.database import create_db_and_tables
        from app.seed import seed_data as run_seed

        with Session(engine) as session:
            # Borrar todo en orden (por FK)
            session.query(AuditLog).delete()
            session.query(EvidenceFile).delete()
            session.query(SprintTask).delete()
            session.query(Sprint).delete()
            session.query(RFC).delete()
            session.query(DocumentVersion).delete()
            session.query(Document).delete()
            session.query(ControlResponse).delete()
            session.query(Evaluation).delete()
            # No borrar usuarios ni clientes base (los recrea el seed)
            session.commit()

            # Recrear tablas y seed
            create_db_and_tables()
            run_seed()

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Base de datos reseteada completamente. Seed ejecutado.",
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)},
        )


@router.get("/ai-config", response_class=HTMLResponse)
def ai_configuration(request: Request):
    """Panel de configuración de Inteligencia Artificial"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    if user.role != UserRole.SUPERADMIN:
        return RedirectResponse(url="/dashboard")

    return render(
        request,
        "admin/ai_config.html",
    )
