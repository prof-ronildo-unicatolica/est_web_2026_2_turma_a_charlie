from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_senha
from app.models.usuario import Usuario


def seed_initial_admin() -> None:
    email = settings.INITIAL_ADMIN_EMAIL
    password = settings.INITIAL_ADMIN_PASSWORD
    name = settings.INITIAL_ADMIN_NAME
    if not email and not password:
        return
    if not email or not password or len(password) < 12:
        raise RuntimeError("Configure INITIAL_ADMIN_EMAIL e INITIAL_ADMIN_PASSWORD (mínimo de 12 caracteres) juntos.")

    normalized_email = email.strip().lower()
    with SessionLocal() as db:
        admin = db.execute(select(Usuario).where(Usuario.email == normalized_email)).scalar_one_or_none()
        if admin:
            if not admin.is_admin:
                admin.is_admin = True
                db.commit()
            return
        db.add(Usuario(
            nome=(name or "Administrador").strip(),
            email=normalized_email,
            senha_hash=hash_senha(password),
            is_admin=True,
        ))
        db.commit()
