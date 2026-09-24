from sqlalchemy.orm import Session

from app.repositories.quarto_repository import QuartoRepository


class QuartoService:
    def __init__(self, db: Session):
        self.repository = QuartoRepository(db)

    def create(self, payload):
        return self.repository.create(
            hotel_id=payload.hotel_id,
            tipo=payload.tipo,
            preco_diaria=payload.preco_diaria,
            max_adultos=payload.max_adultos,
            max_criancas=payload.max_criancas,
        )

    def list(self):
        return self.repository.list()

    def get_by_id(self, quarto_id):
        return self.repository.get_by_id(quarto_id)
    
    def update(self, quarto_id, payload):
        quarto = self.repository.get_by_id(quarto_id)

        if not quarto:
            return None

        dados = payload.model_dump(exclude_unset=True)

        return self.repository.update(quarto, dados)
    
    def delete(self, quarto_id):
        quarto = self.repository.get_by_id(quarto_id)

        if not quarto:
            return None

        self.repository.delete(quarto)

        return quarto