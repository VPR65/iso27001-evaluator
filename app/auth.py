import secrets
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from sqlmodel import Session, select
from app.models import User, Session as UserSession, UserRole
from app.database import engine

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

SESSION_COOKIE_NAME = "session_id"
SESSION_EXPIRE_HOURS = 8


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def create_session(user: User) -> UserSession:
    with Session(engine) as session:
        db_session = UserSession(
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=SESSION_EXPIRE_HOURS),
        )
        session.add(db_session)
        session.commit()
        session.refresh(db_session)
        return db_session


def get_session(session_id: str) -> Optional[UserSession]:
    with Session(engine) as session:
        stmt = select(UserSession).where(UserSession.id == session_id)
        db_session = session.exec(stmt).first()
        if not db_session:
            return None
        if db_session.expires_at < datetime.utcnow():
            session.delete(db_session)
            session.commit()
            return None
        return db_session


def delete_session(session_id: str) -> None:
    with Session(engine) as session:
        stmt = select(UserSession).where(UserSession.id == session_id)
        db_session = session.exec(stmt).first()
        if db_session:
            session.delete(db_session)
            session.commit()


def get_current_user(session_id: Optional[str]) -> Optional[User]:
    if not session_id:
        return None
    db_session = get_session(session_id)
    if not db_session:
        return None
    with Session(engine) as session:
        user = session.get(User, db_session.user_id)
        if not user or not user.is_active:
            return None
        return user


def require_auth(user):
    if not user:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="No autenticado")


def require_role(user, roles):
    require_auth(user)
    if user.role not in roles:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Sin permisos suficientes")


def require_superadmin(user):
    require_role(user, [UserRole.SUPERADMIN])


def require_admin(user):
    require_role(user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE])


def require_no_vista_solo(user):
    require_role(
        user, [UserRole.SUPERADMIN, UserRole.ADMIN_CLIENTE, UserRole.EVALUADOR]
    )
