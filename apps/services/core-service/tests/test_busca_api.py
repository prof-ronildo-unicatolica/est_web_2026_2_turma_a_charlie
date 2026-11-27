
import asyncio
from unittest.mock import AsyncMock, Mock

import app.api.v1.busca as busca_api


def test_buscar_hoteis_chama_service_com_filtros(monkeypatch):
    mongo_db = Mock()

    service = Mock()
    service.buscar_hoteis = AsyncMock(
        return_value=[{"nome": "Hotel Central"}]
    )

    def criar_service(db):
        assert db is mongo_db
        return service

    monkeypatch.setattr(
        busca_api,
        "BuscaService",
        criar_service,
    )

    resultado = asyncio.run(
        busca_api.buscar_hoteis(
            cidade_id="cidade-123",
            estrelas=4,
            mongo_db=mongo_db,
        )
    )

    service.buscar_hoteis.assert_awaited_once_with(
        cidade_id="cidade-123",
        estrelas=4,
    )

    assert resultado == [{"nome": "Hotel Central"}]
