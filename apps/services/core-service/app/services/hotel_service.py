from sqlalchemy.orm import Session

from app.models.hotel import Cidade, Hotel
from app.repositories.hotel_repository import CidadeRepository, HotelRepository

# --- Excecoes de dominio -----------------------------------------------------
# Nao herdam de HTTPException de proposito: o service nao conhece HTTP.
# Quem traduz isto em status code e a camada de rota (issues #15 e #16).


class RegraDeNegocioError(Exception):
    """Base de todas as excecoes de negocio deste modulo."""


class CidadeJaExisteError(RegraDeNegocioError):
    pass


class CidadeNaoEncontradaError(RegraDeNegocioError):
    pass


# --- Services ----------------------------------------------------------------


class CidadeService:
    def __init__(self, db: Session):
        self.repository = CidadeRepository(db)

    def criar(self, nome: str) -> Cidade:
        # Normalizacao ANTES de qualquer validacao: " fortaleza " e "Fortaleza"
        # sao a mesma cidade para um ser humano, mas nao para o UNIQUE do banco.
        nome = nome.strip()

        if self.repository.get_by_nome(nome):
            raise CidadeJaExisteError(f"Ja existe uma cidade chamada '{nome}'.")

        return self.repository.create(nome=nome)

    def listar(self) -> list[Cidade]:
        return self.repository.list()


class HotelService:
    def __init__(self, db: Session):
        self.repository = HotelRepository(db)
        # O HotelService precisa CONSULTAR cidades para validar o vinculo.
        # Ele usa o repository de cidade, e nao o CidadeService: dependencia
        # entre services vira ciclo com facilidade.
        self.cidades = CidadeRepository(db)

    def criar(self, nome: str, cidade_id) -> Hotel:
        nome = nome.strip()

        # A validacao que faltava na issue #13. Sem ela, um UUID inexistente
        # estoura como IntegrityError cru do PostgreSQL -> resposta 500.
        # Com ela, vira um 404 com mensagem legivel.
        if not self.cidades.get_by_id(cidade_id):
            raise CidadeNaoEncontradaError(
                f"Nao existe cidade com id '{cidade_id}'."
            )

        return self.repository.create(nome=nome, cidade_id=cidade_id)

    def listar(self, cidade_id=None) -> list[Hotel]:
        # Um metodo so, com filtro opcional: e o que a rota GET /hoteis
        # precisa para aceitar ?cidade_id=... sem duplicar codigo.
        if cidade_id is not None:
            if not self.cidades.get_by_id(cidade_id):
                raise CidadeNaoEncontradaError(
                    f"Nao existe cidade com id '{cidade_id}'."
                )
            return self.repository.list_by_cidade(cidade_id)
        return self.repository.list()