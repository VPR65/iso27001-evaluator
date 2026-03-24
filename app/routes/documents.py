from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from sqlalchemy import desc
from app.models import (
    Document,
    DocumentVersion,
    Client,
    User,
    UserRole,
    DocumentState,
    AuditLog,
)
from app.auth import get_current_user, require_no_vista_solo, require_role
from app.database import engine
from app.templates_core import render
from app.security import verify_csrf_token
import hashlib
import difflib

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_class=HTMLResponse)
def list_documents(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            docs = session.exec(
                select(Document).order_by(Document.created_at.desc())
            ).all()
        else:
            docs = session.exec(
                select(Document)
                .where(Document.client_id == user.client_id)
                .order_by(Document.created_at.desc())
            ).all()

        docs_data = []
        for d in docs:
            latest = session.exec(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == d.id)
                .order_by(DocumentVersion.created_at.desc())
            ).first()
            version_count = len(
                session.exec(
                    select(DocumentVersion).where(DocumentVersion.document_id == d.id)
                ).all()
            )
            docs_data.append(
                {"doc": d, "latest": latest, "version_count": version_count}
            )

    return render(request, "documents/list.html", documents=docs_data)


@router.get("/new", response_class=HTMLResponse)
def new_document_form(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)
    with Session(engine) as session:
        if user.role == UserRole.SUPERADMIN:
            clients = session.exec(select(Client)).all()
        else:
            clients = [session.get(Client, user.client_id)] if user.client_id else []
    return render(
        request, "documents/form.html", clients=clients, doc=None, errors=None
    )


@router.post("/new")
async def create_document(request: Request):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    title = form_data.get("title")
    document_type = form_data.get("document_type")
    client_id = form_data.get("client_id")
    content = form_data.get("content", "")
    change_summary = form_data.get("change_summary", "Nueva version inicial")

    if user.role != UserRole.SUPERADMIN and user.client_id != client_id:
        raise HTTPException(status_code=403)

    with Session(engine) as session:
        doc = Document(
            title=title,
            document_type=document_type,
            client_id=client_id,
            created_by=user.id,
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        v = DocumentVersion(
            document_id=doc.id,
            version="1.0.0",
            state=DocumentState.DRAFT,
            author_id=user.id,
            content=content,
            change_summary=change_summary,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
        )
        session.add(v)
        session.add(
            AuditLog(
                user_id=user.id,
                action="DOCUMENT_CREATED",
                entity_type="document",
                entity_id=doc.id,
                details=f"Documento creado: {title} (tipo: {document_type})",
            )
        )
        session.commit()
    return RedirectResponse(url="/documents", status_code=302)


@router.get("/{doc_id}", response_class=HTMLResponse)
def view_document(request: Request, doc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")
    require_no_vista_solo(user)

    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc or (
            user.role != UserRole.SUPERADMIN and doc.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        versions = session.exec(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == doc_id)
            .order_by(DocumentVersion.created_at.desc())
        ).all()
    return render(request, "documents/detail.html", doc=doc, versions=versions)


@router.get("/{doc_id}/version/{version_id}", response_class=HTMLResponse)
def view_version(request: Request, doc_id: str, version_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        return RedirectResponse(url="/login")

    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc or (
            user.role != UserRole.SUPERADMIN and doc.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        version = session.get(DocumentVersion, version_id)
        if not version or version.document_id != doc_id:
            raise HTTPException(status_code=404)
        prev_version = session.exec(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id == doc_id,
                DocumentVersion.created_at < version.created_at,
            )
            .order_by(DocumentVersion.created_at.desc())
        ).first()
        diff_text = ""
        if prev_version:
            d = difflib.unified_diff(
                prev_version.content.splitlines() or [""],
                version.content.splitlines() or [""],
                fromfile=f"v{prev_version.version}",
                tofile=f"v{version.version}",
                lineterm="",
            )
            diff_text = "\n".join(d)

    return render(
        request,
        "documents/version.html",
        doc=doc,
        version=version,
        diff=diff_text,
        prev_version=prev_version,
    )


@router.post("/{doc_id}/version")
async def new_version(request: Request, doc_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_no_vista_solo(user)

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    content = form_data.get("content")
    change_summary = form_data.get("change_summary")
    state = form_data.get("state", "draft")

    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc or (
            user.role != UserRole.SUPERADMIN and doc.client_id != user.client_id
        ):
            raise HTTPException(status_code=404)
        latest = session.exec(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == doc_id)
            .order_by(DocumentVersion.created_at.desc())
        ).first()
        major, minor = 1, 0
        if latest:
            parts = latest.version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) + 1
        v = DocumentVersion(
            document_id=doc_id,
            version=f"{major}.{minor}.0",
            state=DocumentState(state),
            author_id=user.id,
            content=content,
            change_summary=change_summary,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            previous_version_id=latest.id if latest else None,
        )
        session.add(v)
        session.add(
            AuditLog(
                user_id=user.id,
                action="DOCUMENT_VERSION_CREATED",
                entity_type="document_version",
                entity_id=v.id,
                details=f"Nueva version {v.version} del documento {doc_id}: {change_summary}",
            )
        )
        session.commit()
    return RedirectResponse(url=f"/documents/{doc_id}", status_code=302)


@router.post("/{doc_id}/version/{version_id}/approve")
async def approve_version(request: Request, doc_id: str, version_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    from datetime import datetime

    with Session(engine) as session:
        v = session.get(DocumentVersion, version_id)
        if v and v.document_id == doc_id:
            v.state = DocumentState.APPROVED
            v.approver_id = user.id
            v.approved_at = datetime.utcnow()
            session.add(v)
            session.add(
                AuditLog(
                    user_id=user.id,
                    action="DOCUMENT_VERSION_APPROVED",
                    entity_type="document_version",
                    entity_id=version_id,
                    details=f"Version {v.version} del documento {doc_id} aprobada",
                )
            )
            session.commit()
    return RedirectResponse(
        url=f"/documents/{doc_id}/version/{version_id}", status_code=302
    )


@router.post("/{doc_id}/version/{version_id}/publish")
async def publish_version(request: Request, doc_id: str, version_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    from datetime import datetime

    with Session(engine) as session:
        v = session.get(DocumentVersion, version_id)
        if v and v.document_id == doc_id:
            v.state = DocumentState.PUBLISHED
            v.published_at = datetime.utcnow()
            session.add(v)
            session.add(
                AuditLog(
                    user_id=user.id,
                    action="DOCUMENT_VERSION_PUBLISHED",
                    entity_type="document_version",
                    entity_id=version_id,
                    details=f"Version {v.version} del documento {doc_id} publicada",
                )
            )
            session.commit()
    return RedirectResponse(url=f"/documents/{doc_id}", status_code=302)


@router.post("/{doc_id}/version/{version_id}/rollback")
async def rollback_version(request: Request, doc_id: str, version_id: str):
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])

    form_data = await request.form()
    csrf_token = form_data.get("csrf_token")
    if not csrf_token or not verify_csrf_token(csrf_token):
        raise HTTPException(status_code=403, detail="Token CSRF invalido")

    with Session(engine) as session:
        source = session.get(DocumentVersion, version_id)
        if not source or source.document_id != doc_id:
            raise HTTPException(status_code=404)
        latest = session.exec(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == doc_id)
            .order_by(DocumentVersion.created_at.desc())
        ).first()
        major = int(source.version.split(".")[0]) + 1
        new_v = DocumentVersion(
            document_id=doc_id,
            version=f"{major}.0.0",
            state=DocumentState.DRAFT,
            author_id=user.id,
            content=source.content,
            change_summary=f"Rollback a version {source.version}",
            content_hash=source.content_hash,
            previous_version_id=latest.id if latest else None,
        )
        session.add(new_v)
        session.add(
            AuditLog(
                user_id=user.id,
                action="DOCUMENT_VERSION_ROLLBACK",
                entity_type="document_version",
                entity_id=new_v.id,
                details=f"Rollback a version {source.version} del documento {doc_id}",
            )
        )
        session.commit()
    return RedirectResponse(url=f"/documents/{doc_id}", status_code=302)
