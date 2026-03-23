from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.security import get_csrf_token

BASE_DIR = Path(__file__).parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def render(request: Request, template_name: str, user=None, **kwargs):
    from app.auth import get_current_user, SESSION_COOKIE_NAME

    if user is None:
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        user = get_current_user(session_id)
    ctx = {"request": request, "user": user, "csrf_token": get_csrf_token()}
    ctx.update(kwargs)
    return templates.TemplateResponse(template_name, ctx)


def setup_templates(app: FastAPI):
    uploads_dir = BASE_DIR.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    return templates


def setup_directories():
    for d in [
        "uploads",
        "backups",
        "backups/auto",
        "backups/deploy",
        "backups/rfc",
        "backups/manual",
    ]:
        p = BASE_DIR.parent / d
        p.mkdir(exist_ok=True)
