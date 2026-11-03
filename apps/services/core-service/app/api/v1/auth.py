from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import (
    autenticar_credenciais,
    get_current_admin,
    get_current_user,
)
from app.core.database import get_db
from app.core.security import criar_access_token, hash_senha
from app.models.usuario import Usuario
from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioPublic




router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
def register(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
):
    """Cadastra um novo usuário."""

    usuario_existente = db.execute(
        select(Usuario).where(Usuario.email == payload.email)
    ).scalar_one_or_none()

    if usuario_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    novo_usuario = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        is_admin=payload.is_admin,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario

@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """Autentica o usuário e retorna um JWT."""

    usuario = autenticar_credenciais(
        payload.email,
        payload.senha,
        db,
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = criar_access_token(
        {"sub": usuario.email}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UsuarioPublic)
def get_me(
    usuario_atual: Usuario = Depends(get_current_user),
):
    """Retorna o perfil do usuário autenticado."""

    return usuario_atual


@router.get("/admin/verificacao")
def somente_admin(
    admin: Usuario = Depends(get_current_admin),
):
    """Rota disponível somente para administradores."""

    return {
        "mensagem": f"Acesso administrativo concedido para {admin.nome}"
    }