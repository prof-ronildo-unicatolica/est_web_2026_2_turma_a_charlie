
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


def test_criar_cidade(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/cidades",
        json={"nome": "Fortaleza", "estado": "CE"},
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Fortaleza"
    assert resposta.json()["estado"] == "CE"


def test_criar_cidade_com_nome_vazio(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/cidades",
        json={"nome": "   ", "estado": "CE"},
        headers=headers,
    )

    assert resposta.status_code == 422


def test_criar_cidade_duplicada(client):
    headers = obter_headers(client)

    dados = {"nome": "Fortaleza", "estado": "CE"}

    client.post(
        "/api/v1/cidades",
        json=dados,
        headers=headers,
    )

    resposta = client.post(
        "/api/v1/cidades",
        json=dados,
        headers=headers,
    )

    assert resposta.status_code == 409


def test_criar_cidade_remove_espacos_do_nome(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/cidades",
        json={"nome": "  Fortaleza  ", "estado": "CE"},
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Fortaleza"


def test_listar_cidades(client):
    headers = obter_headers(client)

    client.post(
        "/api/v1/cidades",
        json={"nome": "Fortaleza", "estado": "CE"},
        headers=headers,
    )

    resposta = client.get("/api/v1/cidades")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Fortaleza"
