
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


def preparar_hotel(client):
    headers = obter_headers(client)

    cidade = client.post(
        "/api/v1/cidades",
        json={
            "nome": "Fortaleza",
            "estado": "CE",
        },
        headers=headers,
    )

    assert cidade.status_code == 201

    hotel = client.post(
        "/api/v1/hoteis",
        json={
            "nome": "Hotel Teste",
            "cidade_id": cidade.json()["id"],
            "categoria_estrelas": 4,
            "comodidade_ids": [],
        },
        headers=headers,
    )

    assert hotel.status_code == 201
    return hotel.json()

@pytest.fixture
def simular_sincronizacao_mongo(monkeypatch):
    async def sincronizar_hotel(self, hotel_id):
        return None

    monkeypatch.setattr(
        "app.services.quarto_service.CatalogoSyncService.sincronizar_hotel",
        sincronizar_hotel,
    )

    monkeypatch.setattr(
        "app.api.v1.quartos.get_mongo_db",
        lambda: {"catalogo_hoteis": object()},
    )


def criar_quarto(client, hotel_id, headers):
    return client.post(
        "/api/v1/quartos",
        json={
            "hotel_id": hotel_id,
            "tipo": "Suíte",
            "preco_diaria": "250.00",
            "max_adultos": 2,
            "max_criancas": 1,
        },
        headers=headers,
    )


def test_criar_quarto(client, simular_sincronizacao_mongo):
    hotel = preparar_hotel(client)
    headers = obter_headers(client)

    resposta = criar_quarto(client, hotel["id"], headers)

    assert resposta.status_code == 201
    assert resposta.json()["tipo"] == "Suíte"
    assert resposta.json()["preco_diaria"] == "250.00"
    assert resposta.json()["hotel_id"] == hotel["id"]


def test_criar_quarto_sem_autenticacao(
    client,
    simular_sincronizacao_mongo,
):
    hotel = preparar_hotel(client)

    resposta = criar_quarto(client, hotel["id"], {})

    assert resposta.status_code in (401, 403)


def test_criar_quarto_com_dados_invalidos(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/quartos",
        json={
            "hotel_id": "00000000-0000-0000-0000-000000000000",
            "tipo": "",
            "preco_diaria": -10,
            "max_adultos": 0,
            "max_criancas": -1,
        },
        headers=headers,
    )

    assert resposta.status_code == 422


def test_listar_quartos(client, simular_sincronizacao_mongo):
    hotel = preparar_hotel(client)
    headers = obter_headers(client)

    criar_quarto(client, hotel["id"], headers)

    resposta = client.get("/api/v1/quartos")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["tipo"] == "Suíte"


def test_buscar_quarto(client, simular_sincronizacao_mongo):
    hotel = preparar_hotel(client)
    headers = obter_headers(client)

    criada = criar_quarto(client, hotel["id"], headers)
    quarto_id = criada.json()["id"]

    resposta = client.get(f"/api/v1/quartos/{quarto_id}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == quarto_id


def test_buscar_quarto_inexistente(
    client,
    simular_sincronizacao_mongo,
):
    resposta = client.get(
        "/api/v1/quartos/00000000-0000-0000-0000-000000000000"
    )

    assert resposta.status_code == 404


def test_atualizar_quarto(client, simular_sincronizacao_mongo):
    hotel = preparar_hotel(client)
    headers = obter_headers(client)

    criada = criar_quarto(client, hotel["id"], headers)
    quarto_id = criada.json()["id"]

    resposta = client.put(
        f"/api/v1/quartos/{quarto_id}",
        json={"tipo": "Suíte Premium"},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["tipo"] == "Suíte Premium"


def test_atualizar_quarto_inexistente(
    client,
    simular_sincronizacao_mongo,
):
    headers = obter_headers(client)

    resposta = client.put(
        "/api/v1/quartos/00000000-0000-0000-0000-000000000000",
        json={"tipo": "Suíte Premium"},
        headers=headers,
    )

    assert resposta.status_code == 404


def test_excluir_quarto(client, simular_sincronizacao_mongo):
    hotel = preparar_hotel(client)
    headers = obter_headers(client)

    criada = criar_quarto(client, hotel["id"], headers)
    quarto_id = criada.json()["id"]

    resposta = client.delete(
        f"/api/v1/quartos/{quarto_id}",
        headers=headers,
    )

    assert resposta.status_code == 204

    consulta = client.get(f"/api/v1/quartos/{quarto_id}")
    assert consulta.status_code == 404


def test_excluir_quarto_inexistente(
    client,
    simular_sincronizacao_mongo,
):
    headers = obter_headers(client)

    resposta = client.delete(
        "/api/v1/quartos/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )

    assert resposta.status_code == 404

def test_criar_quarto_com_erro_interno(
    client,
    simular_sincronizacao_mongo,
    monkeypatch,
):
    async def falhar_ao_criar(self, payload):
        raise RuntimeError("Erro simulado")

    monkeypatch.setattr(
        "app.api.v1.quartos.QuartoService.create",
        falhar_ao_criar,
    )

    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/quartos",
        json={
            "hotel_id": "00000000-0000-0000-0000-000000000000",
            "tipo": "Suíte",
            "preco_diaria": "250.00",
            "max_adultos": 2,
            "max_criancas": 1,
        },
        headers=headers,
    )

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Não foi possível criar o quarto."