from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import jinja2
from starlette.responses import HTMLResponse
from app.security import get_csrf_token

BASE_DIR = Path(__file__).parent

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=jinja2.select_autoescape(default=False, default_for_string=False),
)


def render(request: Request, template_name: str, user=None, **kwargs):
    from app.auth import get_current_user, SESSION_COOKIE_NAME

    if user is None:
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        user = get_current_user(session_id)
    ctx = {"request": request, "user": user, "csrf_token": get_csrf_token()}
    ctx.update(kwargs)
    template = _jinja_env.get_template(template_name)
    html = template.render(ctx)
    return HTMLResponse(html)


def setup_templates(app: FastAPI):
    from starlette.templating import Jinja2Templates

    uploads_dir = BASE_DIR.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
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
