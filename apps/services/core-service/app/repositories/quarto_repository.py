from typing import List

from sqlalchemy.orm import Session

from app.models.hotel import Quarto


class QuartoRepository:
    """Acesso ao banco para Quarto."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        hotel_id,
        tipo: str,
        preco_diaria,
        max_adultos: int,
        max_criancas: int,
    ) -> Quarto:
        quarto = Quarto(
            hotel_id=hotel_id,
            tipo=tipo,
            preco_diaria=preco_diaria,
            max_adultos=max_adultos,
            max_criancas=max_criancas,
        )
        self.db.add(quarto)
        self.db.commit()
        self.db.refresh(quarto)
        return quarto

    def list(self) -> List[Quarto]:
        return self.db.query(Quarto).order_by(Quarto.tipo).all()

    def get_by_id(self, quarto_id) -> Quarto | None:
        return (
            self.db.query(Quarto)
            .filter(Quarto.id == quarto_id)
            .first()
        )
   
    def update(self, quarto: Quarto, dados: dict) -> Quarto:
        for campo, valor in dados.items():
            setattr(quarto, campo, valor)

        self.db.commit()
        self.db.refresh(quarto)

        return quarto
 
    def delete(self, quarto: Quarto) -> None:
        self.db.delete(quarto)
        self.db.commit()