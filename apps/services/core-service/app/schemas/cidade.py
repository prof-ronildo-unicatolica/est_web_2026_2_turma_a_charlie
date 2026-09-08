from pydantic import BaseModel


class CidadeBase(BaseModel):
    nome: str
    estado: str


class CidadeCreate(CidadeBase):
    pass


class CidadePublic(CidadeBase):
    id: int