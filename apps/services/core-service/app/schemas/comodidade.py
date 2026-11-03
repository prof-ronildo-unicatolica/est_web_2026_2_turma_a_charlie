from pydantic import BaseModel, ConfigDict, Field


class ComodidadeBase(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class ComodidadeCreate(ComodidadeBase):
    pass


class ComodidadeUpdate(ComodidadeBase):
    pass


class ComodidadePublic(ComodidadeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int