from sqlalchemy.orm import Session

from app.models.hotel import Cidade


class CidadeRepository:
    """Acesso ao banco para a entidade Cidade. Sem regra de negocio aqui."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str) -> Cidade:
        cidade = Cidade(nome=nome)
        self.db.add(cidade)
        self.db.commit()
        self.db.refresh(cidade)
        return cidade

    def list(self) -> list[Cidade]:
        return self.db.query(Cidade).order_by(Cidade.nome).all()

    def get_by_id(self, cidade_id) -> Cidade | None:
        """Devolve None quando nao existe."""
        return self.db.query(Cidade).filter(Cidade.id == cidade_id).first()

    def get_by_nome(self, nome: str) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.nome == nome).first() 