
import pytest


def obter_headers(client):
    resposta = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@hotel.com",
            "senha": "admin123",
        },
    )

    assert resposta.status_code == 200

    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def criar_cidade(client):
    resposta = client.post(
        "/api/v1/cidades",
        json={
            "nome": "Fortaleza",
            "estado": "CE",
        },
        headers=obter_headers(client),
    )

    assert resposta.status_code == 201
    return resposta.json()


@pytest.fixture
def simular_sincronizacao_mongo(monkeypatch):
    async def sincronizar_hotel(self, hotel_id):
        return None

    monkeypatch.setattr(
        "app.services.hotel_service.CatalogoSyncService.sincronizar_hotel",
        sincronizar_hotel,
    )


def criar_hotel(client, cidade_id, comodidade_ids=None):
    return client.post(
        "/api/v1/hoteis",
        json={
            "nome": "Hotel Teste",
            "cidade_id": cidade_id,
            "categoria_estrelas": 4,
            "comodidade_ids": comodidade_ids or [],
        },
        headers=obter_headers(client),
    )


def test_criar_hotel(client, simular_sincronizacao_mongo):
    cidade = criar_cidade(client)

    resposta = criar_hotel(client, cidade["id"])

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Hotel Teste"
    assert resposta.json()["categoria_estrelas"] == 4
    assert resposta.json()["cidade"]["nome"] == "Fortaleza"


def test_criar_hotel_com_cidade_inexistente(
    client,
    simular_sincronizacao_mongo,
):
    resposta = criar_hotel(
        client,
        "00000000-0000-0000-0000-000000000000",
    )

    assert resposta.status_code == 404


def test_criar_hotel_com_comodidade_inexistente(
    client,
    simular_sincronizacao_mongo,
):
    cidade = criar_cidade(client)

    resposta = criar_hotel(
        client,
        cidade["id"],
        comodidade_ids=[9999],
    )

    assert resposta.status_code == 422


def test_criar_hotel_com_categoria_invalida(client):
    cidade = criar_cidade(client)

    resposta = client.post(
        "/api/v1/hoteis",
        json={
            "nome": "Hotel Teste",
            "cidade_id": cidade["id"],
            "categoria_estrelas": 8,
            "comodidade_ids": [],
        },
        headers=obter_headers(client),
    )

    assert resposta.status_code == 422


def test_listar_hoteis(client, simular_sincronizacao_mongo):
    cidade = criar_cidade(client)
    criar_hotel(client, cidade["id"])

    resposta = client.get("/api/v1/hoteis")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Hotel Teste"


def test_listar_hoteis_por_cidade(client, simular_sincronizacao_mongo):
    cidade = criar_cidade(client)
    criar_hotel(client, cidade["id"])

    resposta = client.get(
        f"/api/v1/hoteis?cidade_id={cidade['id']}"
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_listar_hoteis_com_cidade_inexistente(client):
    resposta = client.get(
        "/api/v1/hoteis?cidade_id=00000000-0000-0000-0000-000000000000"
    )

    assert resposta.status_code == 404


def test_obter_hotel(client, simular_sincronizacao_mongo):
    cidade = criar_cidade(client)
    criada = criar_hotel(client, cidade["id"])

    hotel_id = criada.json()["id"]

    resposta = client.get(f"/api/v1/hoteis/{hotel_id}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == hotel_id


def test_obter_hotel_inexistente(client):
    resposta = client.get(
        "/api/v1/hoteis/00000000-0000-0000-0000-000000000000"
    )

    assert resposta.status_code == 404


def test_listar_hoteis_por_rota_de_cidade(
    client,
    simular_sincronizacao_mongo,
):
    cidade = criar_cidade(client)
    criar_hotel(client, cidade["id"])

    resposta = client.get(
        f"/api/v1/hoteis/cidades/{cidade['id']}/hoteis"
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_listar_hoteis_por_rota_com_cidade_inexistente(client):
    resposta = client.get(
        "/api/v1/hoteis/cidades/00000000-0000-0000-0000-000000000000/hoteis"
    )

    assert resposta.status_code == 404
