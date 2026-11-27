
from unittest.mock import MagicMock, patch

from app.core.database import get_db, get_mongo_db, mongo_db


def test_get_db_cria_sessao_e_fecha_ao_finalizar():
    sessao = MagicMock()

    with patch("app.core.database.SessionLocal", return_value=sessao):
        gerador = get_db()

        resultado = next(gerador)

        assert resultado is sessao

        gerador.close()

        sessao.close.assert_called_once()


def test_get_mongo_db_retorna_banco():
    resultado = get_mongo_db()

    assert resultado is mongo_db
