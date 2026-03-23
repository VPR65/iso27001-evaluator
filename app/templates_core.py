from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.security import get_csrf_token

BASE_DIR = Path(__file__).parent

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

templates.env.globals["csrf_token"] = lambda: get_csrf_token()


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
