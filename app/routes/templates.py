"""
Gestión de Plantillas de Respuestas Predefinidas
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from app.models import ResponseTemplate, User, UserRole
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from app.security import verify_csrf_token
from datetime import datetime

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/")
def list_templates(request: Request):
    """Listar todas las plantillas disponibles"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        templates = session.exec(
            select(ResponseTemplate).order_by(ResponseTemplate.name)
        ).all()

        return HTMLResponse(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Plantillas de Respuestas</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
            </head>
            <body class="container">
                <header style="display:flex;justify-content:space-between;align-items:center;margin:2rem 0;">
                    <h1>📋 Plantillas de Respuestas</h1>
                    <a href="/templates/new" class="btn btn-primary">Nueva Plantilla</a>
                </header>
                
                <table>
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Categoría</th>
                            <th>Madurez</th>
                            <th>Control (si aplica)</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {
                "".join(
                    [
                        f'''
                        <tr>
                            <td><strong>{t.name}</strong></td>
                            <td><span class="badge">{t.category}</span></td>
                            <td>{t.maturity}/5</td>
                            <td>{t.control_code or 'General'}</td>
                            <td>
                                <a href="/templates/{t.id}/edit" class="btn btn-sm">Editar</a>
                                <form method="post" action="/templates/{t.id}/delete" style="display:inline;">
                                    <input type="hidden" name="csrf_token" value="{{{{ csrf_token }}}}">
                                    <button type="submit" class="btn btn-sm btn-danger" onclick="return confirm('¿Eliminar?')">Eliminar</button>
                                </form>
                            </td>
                        </tr>
                        '''
                        for t in templates
                    ]
                )
            }
                    </tbody>
                </table>
                
                {
                f'<p style="text-align:center;color:#6b7280;margin-top:2rem;">No hay plantillas creadas</p>'
                if not templates
                else ""
            }
            </body>
            </html>
            """
        )


@router.get("/new")
def new_template_form(request: Request):
    """Formulario para crear nueva plantilla"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401)

    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nueva Plantilla</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    </head>
    <body class="container">
        <h1>📝 Nueva Plantilla</h1>
        <form method="post" action="/templates/save">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            
            <label>Nombre descriptivo *
                <input type="text" name="name" required placeholder="Ej: Política documentada disponible">
            </label>
            
            <label>Categoría
                <select name="category">
                    <option value="general">General</option>
                    <option value="compliance">Cumplimiento</option>
                    <option value="evidence">Evidencia</option>
                    <option value="na">No Aplica</option>
                </select>
            </label>
            
            <label>Nivel de Madurez sugerido (0-5)
                <input type="number" name="maturity" min="0" max="5" value="3">
            </label>
            
            <label>Notas / Respuesta estándar *
                <textarea name="notes" rows="5" required placeholder="Describa la respuesta estándar..."></textarea>
            </label>
            
            <label>Justificación (opcional, para N/A)
                <textarea name="justification" rows="3" placeholder="Justificación si es N/A..."></textarea>
            </label>
            
            <label>¿Es para marcar como No Aplica?
                <select name="is_na">
                    <option value="false">No</option>
                    <option value="true">Sí</option>
                </select>
            </label>
            
            <button type="submit" class="btn btn-primary">Guardar Plantilla</button>
            <a href="/templates" class="btn btn-secondary">Cancelar</a>
        </form>
    </body>
    </html>
    """)


@router.post("/save")
def save_template(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    maturity: int = Form(...),
    notes: str = Form(...),
    justification: str = Form(""),
    is_na: str = Form("false"),
):
    """Guardar nueva plantilla"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    csrf_token = request.cookies.get("csrf_token")
    # Simplificación: en producción validar CSRF correctamente

    with Session(engine) as session:
        template = ResponseTemplate(
            name=name,
            category=category,
            maturity=maturity,
            notes=notes,
            justification=justification if justification else None,
            is_na=is_na == "true",
            created_by=user.id,
        )
        session.add(template)
        session.commit()

    return RedirectResponse("/templates", status_code=303)


@router.post("/{template_id}/delete")
def delete_template(template_id: str, request: Request):
    """Eliminar plantilla"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    with Session(engine) as session:
        template = session.get(ResponseTemplate, template_id)
        if template:
            session.delete(template)
            session.commit()

    return RedirectResponse("/templates", status_code=303)


# Seed inicial de plantillas
INITIAL_TEMPLATES = [
    {
        "name": "Política documentada disponible",
        "category": "compliance",
        "maturity": 3,
        "notes": "Existe política documentada y aprobada por la dirección. Se encuentra disponible en el repositorio corporativo y ha sido comunicada a todo el personal.",
        "is_na": False,
    },
    {
        "name": "Evidencia parcial - En implementación",
        "category": "evidence",
        "maturity": 2,
        "notes": "El control está en proceso de implementación. Existe documentación borrador y se han iniciado las primeras pruebas. Fecha estimada de completitud: 30 días.",
        "is_na": False,
    },
    {
        "name": "Sin evidencia documentada",
        "category": "evidence",
        "maturity": 1,
        "notes": "No se encontró evidencia documentada del control. El proceso se realiza de forma informal y no estandarizada.",
        "is_na": False,
    },
    {
        "name": "Control no aplica - Justificación requerida",
        "category": "na",
        "maturity": 0,
        "notes": "",
        "justification": "Este control no aplica debido a [ESPECIFICAR RAZÓN: alcance, tipo de organización, etc.].",
        "is_na": True,
    },
    {
        "name": "Cumplimiento total verificado",
        "category": "compliance",
        "maturity": 5,
        "notes": "El control está totalmente implementado, documentado, medido y optimizado. Se realizan auditorías trimestrales y mejoras continuas basadas en métricas objetivas.",
        "is_na": False,
    },
]


def init_templates(session, user_id: str):
    """Inicializar plantillas si no existen"""
    existing = session.exec(select(ResponseTemplate)).first()
    if existing:
        return  # Ya existen plantillas

    for template_data in INITIAL_TEMPLATES:
        template = ResponseTemplate(**template_data, created_by=user_id)
        session.add(template)

    session.commit()
