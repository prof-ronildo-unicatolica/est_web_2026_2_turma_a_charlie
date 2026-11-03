from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decodificar_access_token, verificar_senha
from app.models.usuario import Usuario
from app.core.database import get_db

bearer_scheme = HTTPBearer(
    description="Use o token retornado por POST /auth/login"
)


def autenticar_credenciais(
    email: str,
    senha: str,
    db: Session,
) -> Usuario | None:
    """Busca o usuário no banco e verifica a senha com bcrypt."""

    resultado = db.execute(
        select(Usuario).where(Usuario.email == email)
    )

    usuario = resultado.scalar_one_or_none()

    if usuario is None:
        return None

    if not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida o JWT e retorna o usuário autenticado."""

    token = credentials.credentials

    payload = decodificar_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    resultado = db.execute(
        select(Usuario).where(Usuario.email == email)
    )

    usuario = resultado.scalar_one_or_none()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def get_current_admin(
    usuario: Usuario = Depends(get_current_user),
) -> Usuario:
    """Permite acesso somente para usuários administradores."""

    if not usuario.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )

    return usuario