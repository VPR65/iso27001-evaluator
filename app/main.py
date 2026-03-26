"""
ISO 27001 Evaluator - Sistema de evaluacion de controles de seguridad
Version: 1.3.0
Fecha: 2026-03-24
Autor: Equipo de Desarrollo

Este modulo es el punto de entrada de la aplicacion FastAPI.
Configura todos los middlewares, routers y servicios.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import create_db_and_tables
from app.seed import seed_data
from app.templates_core import setup_templates, setup_directories

# Configuracion de seguridad CSRF
# Usamos secret key para generar tokens CSRF en formularios
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

app = FastAPI(
    title="ISO 27001 Evaluator",
    version="1.1.2",
    description="Sistema web para evaluar el cumplimiento de seguridad bajo ISO 27001:2022",
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_directories()
templates = setup_templates(app)

static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

uploads_path = Path(__file__).parent.parent / "uploads"
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_data()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root(request: Request):
    from app.auth import get_current_user, SESSION_COOKIE_NAME

    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard")


from app.routes import (
    auth,
    dashboard,
    clients,
    users,
    evaluations,
    evaluate,
    stats,
    import_export,
)
from app.routes import documents, rfcs, sprints, admin, biblioteca
from app.routes import ai_routes

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(clients.router)
app.include_router(users.router)
app.include_router(evaluations.router)
app.include_router(evaluate.router)
app.include_router(stats.router)
app.include_router(import_export.router)
app.include_router(biblioteca.router)
app.include_router(documents.router)
app.include_router(rfcs.router)
app.include_router(sprints.router)
app.include_router(admin.router)
app.include_router(ai_routes.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", reload=True)
