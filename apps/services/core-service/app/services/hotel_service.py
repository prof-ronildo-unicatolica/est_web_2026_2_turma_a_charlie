from sqlalchemy.orm import Session

from app.models.hotel import Cidade, Hotel
from app.repositories.hotel_repository import CidadeRepository, HotelRepository


class RegraDeNegocioError(Exception):
    """Base de todas as exceções de negócio deste módulo."""


class CidadeJaExisteError(RegraDeNegocioError):
    pass


class CidadeNaoEncontradaError(RegraDeNegocioError):
    pass


class CidadeService:
    def __init__(self, db: Session):
        self.repository = CidadeRepository(db)

    def criar(self, nome: str, estado: str) -> Cidade:
        nome = nome.strip()

        if self.repository.get_by_nome(nome):
            raise CidadeJaExisteError(
                f"Já existe uma cidade chamada '{nome}'."
            )

        return self.repository.create(
            nome=nome,
            estado=estado,
        )

    def listar(self) -> list[Cidade]:
        return self.repository.list()

    def get_by_id(self, cidade_id):
        return self.repository.get_by_id(cidade_id)

    def get_by_nome(self, nome: str):
        return self.repository.get_by_nome(nome)


class HotelService:
    def __init__(self, db: Session):
        self.repository = HotelRepository(db)
        self.cidades = CidadeRepository(db)

    def criar(
        self,
        nome: str,
        cidade_id,
        categoria_estrelas: int,
    ) -> Hotel:
        nome = nome.strip()

        if not self.cidades.get_by_id(cidade_id):
            raise CidadeNaoEncontradaError(
                f"Não existe cidade com id '{cidade_id}'."
            )

        return self.repository.create(
            nome=nome,
            cidade_id=cidade_id,
            categoria_estrelas=categoria_estrelas,
        )

    def listar(self, cidade_id=None) -> list[Hotel]:
        if cidade_id is not None:
            if not self.cidades.get_by_id(cidade_id):
                raise CidadeNaoEncontradaError(
                    f"Não existe cidade com id '{cidade_id}'."
                )

            return self.repository.list_by_cidade(cidade_id)

        return self.repository.list()

    def get_by_id(self, hotel_id):
        return self.repository.get_by_id(hotel_id)