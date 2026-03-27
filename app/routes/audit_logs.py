"""
Auditoría de Logs - Sprint 3.2
Registro y visualización de actividad del sistema
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, func
from app.models import AuditLog, User, Client
from app.auth import get_current_user
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs")
def audit_logs(
    request: Request,
    days: int = 30,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
):
    """
    Ver logs de auditoría
    Params:
    - days: Días hacia atrás (default: 30)
    - user_id: Filtrar por usuario (opcional)
    - action: Filtrar por acción (opcional)
    """
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    # Solo superadmin o admin del cliente puede ver logs
    if user.role.value != "superadmin":
        raise HTTPException(status_code=403, detail="Solo superadmin puede ver logs")

    with Session(engine) as session:
        # Calcular fecha límite
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Construir query base
        query = select(AuditLog).where(AuditLog.created_at >= cutoff_date)

        # Filtros adicionales
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)

        # Ordenar por fecha descendente
        query = query.order_by(AuditLog.created_at.desc())

        # Limitar a 1000 registros para performance
        logs = session.exec(query.limit(1000)).all()

        # Obtener usuarios para mostrar nombres
        user_ids = list(set([log.user_id for log in logs if log.user_id]))
        users_map = {}
        if user_ids:
            users = session.exec(select(User).where(User.id.in_(user_ids))).all()
            users_map = {u.id: u.name for u in users}

        return HTMLResponse(render_audit_logs(logs, users_map, days, user))


def render_audit_logs(logs, users_map, days, current_user):
    """Renderizar tabla de logs de auditoría"""

    # Filas de la tabla
    rows = ""
    for log in logs:
        user_name = users_map.get(log.user_id, log.user_id or "Sistema")
        rows += f"""
        <tr>
            <td>{log.created_at.strftime("%d/%m/%Y %H:%M")}</td>
            <td>{user_name}</td>
            <td><span class="badge">{log.action}</span></td>
            <td>{log.entity_type}</td>
            <td>{log.entity_id or "-"}</td>
            <td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{log.details or "-"}</td>
            <td>{log.ip_address or "-"}</td>
        </tr>
        """

    if not rows:
        rows = "<tr><td colspan='7' style='text-align:center;padding:2rem;'>No hay registros de auditoría en los últimos {days} días</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Auditoría de Logs</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <style>
        .audit-container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
        .filters {{ background: #f9fafb; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; }}
        .stat-value {{ font-size: 2rem; font-weight: 700; color: #1f2937; }}
        .stat-label {{ color: #6b7280; font-size: 0.875rem; }}
        table {{ width: 100%; font-size: 0.875rem; }}
        th {{ white-space: nowrap; }}
        </style>
    </head>
    <body>
        <div class="audit-container">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;">
                <h1>🔍 Auditoría de Logs</h1>
                <div>
                    <a href="/dashboard" class="btn btn-outline">Volver</a>
                    <a href="/audit/logs?days=7" class="btn btn-sm">Últimos 7 días</a>
                    <a href="/audit/logs?days=30" class="btn btn-sm">Últimos 30 días</a>
                    <a href="/audit/logs?days=90" class="btn btn-sm">Últimos 90 días</a>
                </div>
            </div>
            
            <div class="filters">
                <h3>Filtros</h3>
                <form method="get" action="/audit/logs" style="display:flex;gap:1rem;flex-wrap:wrap;">
                    <div>
                        <label>Días
                        <input type="number" name="days" value="{days}" min="1" max="365" style="width:100px;"></label>
                    </div>
                    <div>
                        <label>Usuario
                        <input type="text" name="user_id" placeholder="ID de usuario" style="width:250px;"></label>
                    </div>
                    <div>
                        <label>Acción
                        <select name="action">
                            <option value="">Todas</option>
                            <option value="LOGIN">LOGIN</option>
                            <option value="LOGOUT">LOGOUT</option>
                            <option value="CONTROL_EVALUATED">CONTROL_EVALUATED</option>
                            <option value="CONTROL_UPDATED">CONTROL_UPDATED</option>
                            <option value="EVIDENCE_UPLOADED">EVIDENCE_UPLOADED</option>
                            <option value="USER_CREATED">USER_CREATED</option>
                            <option value="CLIENT_CREATED">CLIENT_CREATED</option>
                        </select></label>
                    </div>
                    <div style="align-self:flex-end;">
                        <button type="submit" class="btn btn-primary">Filtrar</button>
                    </div>
                </form>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(logs)}</div>
                    <div class="stat-label">Total Registros</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len([l for l in logs if l.action == "LOGIN"])}</div>
                    <div class="stat-label">Logins</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len([l for l in logs if l.action == "CONTROL_UPDATED"])}</div>
                    <div class="stat-label">Controles Actualizados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len([l for l in logs if l.action == "EVIDENCE_UPLOADED"])}</div>
                    <div class="stat-label">Evidencias Subidas</div>
                </div>
            </div>
            
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Usuario</th>
                            <th>Acción</th>
                            <th>Entidad</th>
                            <th>ID Entidad</th>
                            <th>Detalles</th>
                            <th>IP</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """


@router.get("/activity")
def user_activity(request: Request):
    """Vista de actividad reciente del usuario actual"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        # Obtener logs del usuario en las últimas 48 horas
        cutoff = datetime.utcnow() - timedelta(hours=48)
        logs = session.exec(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .where(AuditLog.created_at >= cutoff)
            .order_by(AuditLog.created_at.desc())
            .limit(50)
        ).all()

        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mi Actividad Reciente</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        </head>
        <body class="container">
            <h2>📋 Mi Actividad Reciente (48hs)</h2>
            <p>Usuario: <strong>{user.name}</strong> ({user.email})</p>
            
            <p><strong>{len(logs)}</strong> registros encontrados.</p>
            
            <ul>
            {"".join([f"<li>{log.created_at.strftime('%d/%m %H:%M')} - {log.action}: {log.details[:100]}...</li>" for log in logs]) if logs else "<li>No hay actividad reciente</li>"}
            </ul>
            
            <a href="/dashboard" class="btn btn-outline">Volver</a>
        </body>
        </html>
        """)
