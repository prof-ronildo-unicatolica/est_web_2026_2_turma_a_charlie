from datetime import date, timedelta
from decimal import Decimal

from app.models.hotel import Cidade, Hotel, Quarto
from app.models.interacao import Reserva


def criar_hotel_com_quarto(db_session):
    cidade = Cidade(nome="Quixadá", estado="CE")
    db_session.add(cidade)
    db_session.flush()
    hotel = Hotel(nome="Hotel Teste", cidade_id=cidade.id, categoria_estrelas=3)
    db_session.add(hotel)
    db_session.flush()
    quarto = Quarto(
        hotel_id=hotel.id,
        tipo="Standard",
        preco_diaria=Decimal("150.00"),
        max_adultos=2,
        max_criancas=1,
    )
    db_session.add(quarto)
    db_session.commit()
    return hotel, quarto


def token_cliente(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "cliente@hotel.com", "senha": "cliente123"},
    )
    return response.json()["access_token"]


def test_criar_reserva_e_impedir_conflito(client, db_session):
    _, quarto = criar_hotel_com_quarto(db_session)
    token = token_cliente(client)
    headers = {"Authorization": f"Bearer {token}"}
    checkin = date.today() + timedelta(days=10)
    checkout = checkin + timedelta(days=2)
    payload = {
        "quarto_id": str(quarto.id),
        "data_checkin": checkin.isoformat(),
        "data_checkout": checkout.isoformat(),
        "adultos": 2,
        "criancas": 1,
    }

    primeira = client.post("/api/v1/reservas", json=payload, headers=headers)
    assert primeira.status_code == 201
    assert primeira.json()["valor_total"] == 300.0
    assert primeira.json()["status"] == "pendente"

    conflito = client.post("/api/v1/reservas", json=payload, headers=headers)
    assert conflito.status_code == 409


def test_favoritos_persistem_na_conta(client, db_session):
    hotel, _ = criar_hotel_com_quarto(db_session)
    headers = {"Authorization": f"Bearer {token_cliente(client)}"}

    adicionar = client.put(f"/api/v1/favoritos/{hotel.id}", headers=headers)
    assert adicionar.status_code == 200
    assert adicionar.json()["hotel_id"] == str(hotel.id)

    listar = client.get("/api/v1/favoritos", headers=headers)
    assert listar.status_code == 200
    assert [item["hotel_id"] for item in listar.json()] == [str(hotel.id)]

    remover = client.delete(f"/api/v1/favoritos/{hotel.id}", headers=headers)
    assert remover.status_code == 204


def test_avaliacao_exige_hospedagem_concluida(client, db_session):
    hotel, quarto = criar_hotel_com_quarto(db_session)
    usuario = db_session.query(__import__("app.models.usuario", fromlist=["Usuario"]).Usuario).filter_by(email="cliente@hotel.com").first()
    checkout = date.today() - timedelta(days=1)
    checkin = checkout - timedelta(days=2)
    reserva = Reserva(
        usuario_id=usuario.id,
        hotel_id=hotel.id,
        quarto_id=quarto.id,
        data_checkin=checkin,
        data_checkout=checkout,
        adultos=1,
        criancas=0,
        status="confirmada",
        valor_total=300.0,
    )
    db_session.add(reserva)
    db_session.commit()
    headers = {"Authorization": f"Bearer {token_cliente(client)}"}

    response = client.post(
        "/api/v1/avaliacoes",
        json={"hotel_id": str(hotel.id), "nota": 5, "comentario": "Excelente estadia."},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["nota"] == 5
