from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    senha: str


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=100)
    senha: str = Field(min_length=8, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioPublic(BaseModel):
    """Perfil publico do usuario (nunca expoe senha)."""

    email: str
    nome: str
    is_admin: bool
