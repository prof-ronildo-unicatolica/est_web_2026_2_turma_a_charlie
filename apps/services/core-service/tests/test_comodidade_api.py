def obter_headers(client, email="admin@hotel.com", senha="admin123"):
    resposta = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": senha},
    )

    assert resposta.status_code == 200

    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_criar_comodidade(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Wi-Fi"
    assert "id" in resposta.json()


def test_criar_comodidade_com_nome_vazio(client):
    headers = obter_headers(client)

    resposta = client.post(
        "/api/v1/comodidades",
        json={"nome": "   "},
        headers=headers,
    )

    assert resposta.status_code == 422


def test_criar_comodidade_duplicada(client):
    headers = obter_headers(client)

    client.post(
        "/api/v1/comodidades",
        json={"nome": "Piscina"},
        headers=headers,
    )

    resposta = client.post(
        "/api/v1/comodidades",
        json={"nome": "Piscina"},
        headers=headers,
    )

    assert resposta.status_code == 409


def test_listar_comodidades(client):
    headers = obter_headers(client)

    client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    resposta = client.get("/api/v1/comodidades")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Wi-Fi"


def test_atualizar_comodidade(client):
    headers = obter_headers(client)

    criada = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    comodidade_id = criada.json()["id"]

    resposta = client.put(
        f"/api/v1/comodidades/{comodidade_id}",
        json={"nome": "Internet"},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Internet"


def test_atualizar_comodidade_inexistente(client):
    headers = obter_headers(client)

    resposta = client.put(
        "/api/v1/comodidades/9999",
        json={"nome": "Internet"},
        headers=headers,
    )

    assert resposta.status_code == 404


def test_atualizar_comodidade_com_nome_vazio(client):
    headers = obter_headers(client)

    criada = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    comodidade_id = criada.json()["id"]

    resposta = client.put(
        f"/api/v1/comodidades/{comodidade_id}",
        json={"nome": "   "},
        headers=headers,
    )

    assert resposta.status_code == 422


def test_atualizar_comodidade_com_nome_duplicado(client):
    headers = obter_headers(client)

    primeira = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    client.post(
        "/api/v1/comodidades",
        json={"nome": "Piscina"},
        headers=headers,
    )

    resposta = client.put(
        f"/api/v1/comodidades/{primeira.json()['id']}",
        json={"nome": "Piscina"},
        headers=headers,
    )

    assert resposta.status_code == 409


def test_excluir_comodidade(client):
    headers = obter_headers(client)

    criada = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    comodidade_id = criada.json()["id"]

    resposta = client.delete(
        f"/api/v1/comodidades/{comodidade_id}",
        headers=headers,
    )

    assert resposta.status_code == 204

    consulta = client.get("/api/v1/comodidades")
    assert consulta.json() == []


def test_excluir_comodidade_inexistente(client):
    headers = obter_headers(client)

    resposta = client.delete(
        "/api/v1/comodidades/9999",
        headers=headers,
    )

    assert resposta.status_code == 404


def test_criar_comodidade_sem_autenticacao(client):
    resposta = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
    )

    assert resposta.status_code in (401, 403)


def test_criar_comodidade_com_usuario_comum(client):
    headers = obter_headers(
        client,
        email="cliente@hotel.com",
        senha="cliente123",
    )

    resposta = client.post(
        "/api/v1/comodidades",
        json={"nome": "Wi-Fi"},
        headers=headers,
    )

    assert resposta.status_code == 403
