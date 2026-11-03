from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.catalogo_repository import CatalogoRepository


class BuscaService:
    """Regras de negócio da busca pública de hotéis."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repository = CatalogoRepository(db)

    async def buscar_hoteis(
        self,
        cidade_id: str | None = None,
        estrelas: int | None = None,
    ) -> list[dict]:
        filtros = {}

        if cidade_id:
            filtros["cidade_id"] = cidade_id

        if estrelas is not None:
            filtros["categoria_estrelas"] = estrelas

        return await self.repository.buscar(filtros)