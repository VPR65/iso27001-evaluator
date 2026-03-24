from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlmodel import Session, select
from app.models import Biblioteca, Client, User, UserRole, AuditLog
from app.auth import get_current_user
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
import os
import aiofiles
from pathlib import Path

router = APIRouter(prefix="/biblioteca", tags=["biblioteca"])

BIBLIOTECA_DIR = Path("uploads/biblioteca")
BIBLIOTECA_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_class=HTMLResponse)
def list_biblioteca(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            docs = session.exec(
                select(Biblioteca).order_by(Biblioteca.created_at.desc())
            ).all()
            clients_map = {c.id: c for c in session.exec(select(Client)).all()}
        else:
            docs = session.exec(
                select(Biblioteca)
                .where(Biblioteca.client_id == user.client_id)
                .order_by(Biblioteca.created_at.desc())
            ).all()
            clients_map = {user.client_id: session.get(Client, user.client_id)}

        users_map = {u.id: u for u in session.exec(select(User)).all()}

        data = []
        for d in docs:
            data.append(
                {
                    "doc": d,
                    "client": clients_map.get(d.client_id),
                    "uploader": users_map.get(d.uploaded_by),
                }
            )

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []

    return render(request, "biblioteca/list.html", documents=data, clients=clients)


@router.post("/upload")
async def upload_file(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    title = form_data.get("title")
    description = form_data.get("description", "")
    category = form_data.get("category", "general")
    client_id = form_data.get("client_id")
    file: UploadFile = form_data.get("file")

    if not title or not file or not client_id:
        return HTMLResponse("Faltan campos obligatorios", status_code=400)

    if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
        raise HTTPException(status_code=403)

    filename = f"{Path(file.filename).stem}_{user.id[:8]}{Path(file.filename).suffix}"
    filepath = BIBLIOTECA_DIR / filename

    content = await file.read()
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    with Session(engine) as session:
        doc = Biblioteca(
            client_id=client_id,
            title=title,
            description=description,
            category=category,
            filename=file.filename,
            filepath=str(filepath),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            uploaded_by=user.id,
        )
        session.add(doc)
        session.add(
            AuditLog(
                user_id=user.id,
                action="BIBLIOTECA_UPLOAD",
                entity_type="biblioteca",
                entity_id=doc.id,
                details=f"Subio documento: {title} ({file.filename})",
            )
        )
        session.commit()

    return RedirectResponse(url="/biblioteca", status_code=302)


@router.get("/download/{doc_id}")
def download_file(request: Request, doc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        doc = session.get(Biblioteca, doc_id)
        if not doc:
            raise HTTPException(status_code=404)
        if user.role != UserRole.SUPERADMIN and doc.client_id != user.client_id:
            raise HTTPException(status_code=403)

    return FileResponse(doc.filepath, filename=doc.filename, media_type=doc.mime_type)


@router.post("/{doc_id}/delete")
async def delete_file(request: Request, doc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    with Session(engine) as session:
        doc = session.get(Biblioteca, doc_id)
        if not doc:
            raise HTTPException(status_code=404)
        if user.role != UserRole.SUPERADMIN and doc.client_id != user.client_id:
            raise HTTPException(status_code=403)

        filepath = Path(doc.filepath)
        if filepath.exists():
            filepath.unlink()

        session.add(
            AuditLog(
                user_id=user.id,
                action="BIBLIOTECA_DELETE",
                entity_type="biblioteca",
                entity_id=doc_id,
                details=f"Elimino documento: {doc.title}",
            )
        )
        session.delete(doc)
        session.commit()

    return RedirectResponse(url="/biblioteca", status_code=302)
