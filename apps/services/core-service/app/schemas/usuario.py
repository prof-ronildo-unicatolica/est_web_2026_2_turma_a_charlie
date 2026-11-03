from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    is_admin: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioPublic(BaseModel):
    """Perfil publico do usuario (nunca expoe senha)."""

    email: str
    nome: str
    is_admin: bool