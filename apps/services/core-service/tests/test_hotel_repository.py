from uuid import UUID

from app.models.comodidade import Comodidade
from app.repositories.hotel_repository import (
    CidadeRepository,
    HotelRepository,
)


def test_criar_cidade_repository(db_session):
    repository = CidadeRepository(db_session)

    cidade = repository.create(
        nome="Fortaleza",
        estado="CE",
    )

    assert cidade.id is not None
    assert cidade.nome == "Fortaleza"
    assert cidade.estado == "CE"


def test_listar_cidades_repository(db_session):
    repository = CidadeRepository(db_session)

    repository.create("Fortaleza", "CE")
    repository.create("Quixada", "CE")

    cidades = repository.list()

    assert len(cidades) == 2
    assert cidades[0].nome == "Fortaleza"
    assert cidades[1].nome == "Quixada"


def test_buscar_cidade_por_id_repository(db_session):
    repository = CidadeRepository(db_session)

    cidade = repository.create("Fortaleza", "CE")

    resultado = repository.get_by_id(cidade.id)

    assert resultado is not None
    assert resultado.id == cidade.id
    assert resultado.nome == "Fortaleza"


def test_buscar_cidade_inexistente_repository(db_session):
    repository = CidadeRepository(db_session)

    resultado = repository.get_by_id(
        UUID("00000000-0000-0000-0000-000000000000")
    )

    assert resultado is None


def test_buscar_cidade_por_nome_repository(db_session):
    repository = CidadeRepository(db_session)

    repository.create("Fortaleza", "CE")

    resultado = repository.get_by_nome("Fortaleza")

    assert resultado is not None
    assert resultado.nome == "Fortaleza"


def test_criar_hotel_sem_comodidades_repository(db_session):
    cidade_repository = CidadeRepository(db_session)
    hotel_repository = HotelRepository(db_session)

    cidade = cidade_repository.create("Fortaleza", "CE")

    hotel = hotel_repository.create(
        nome="Hotel Central",
        cidade_id=cidade.id,
        categoria_estrelas=4,
    )

    assert hotel.id is not None
    assert hotel.nome == "Hotel Central"
    assert hotel.comodidades == []


def test_criar_hotel_com_comodidades_repository(db_session):
    cidade_repository = CidadeRepository(db_session)
    hotel_repository = HotelRepository(db_session)

    cidade = cidade_repository.create("Fortaleza", "CE")

    wifi = Comodidade(nome="Wi-Fi")
    piscina = Comodidade(nome="Piscina")

    db_session.add_all([wifi, piscina])
    db_session.commit()

    hotel = hotel_repository.create(
        nome="Hotel Central",
        cidade_id=cidade.id,
        categoria_estrelas=4,
        comodidades=[wifi, piscina],
    )

    assert len(hotel.comodidades) == 2
    assert {item.nome for item in hotel.comodidades} == {
        "Wi-Fi",
        "Piscina",
    }


def test_listar_hoteis_repository(db_session):
    cidade_repository = CidadeRepository(db_session)
    hotel_repository = HotelRepository(db_session)

    cidade = cidade_repository.create("Fortaleza", "CE")

    hotel_repository.create("Hotel B", cidade.id, 3)
    hotel_repository.create("Hotel A", cidade.id, 4)

    hoteis = hotel_repository.list()

    assert len(hoteis) == 2
    assert hoteis[0].nome == "Hotel A"
    assert hoteis[1].nome == "Hotel B"


def test_listar_hoteis_por_cidade_repository(db_session):
    cidade_repository = CidadeRepository(db_session)
    hotel_repository = HotelRepository(db_session)

    fortaleza = cidade_repository.create("Fortaleza", "CE")
    quixada = cidade_repository.create("Quixada", "CE")

    hotel_repository.create("Hotel Fortaleza", fortaleza.id, 4)
    hotel_repository.create("Hotel Quixada", quixada.id, 3)

    resultado = hotel_repository.list_by_cidade(fortaleza.id)

    assert len(resultado) == 1
    assert resultado[0].nome == "Hotel Fortaleza"


def test_buscar_hotel_por_id_repository(db_session):
    cidade_repository = CidadeRepository(db_session)
    hotel_repository = HotelRepository(db_session)

    cidade = cidade_repository.create("Fortaleza", "CE")

    hotel = hotel_repository.create(
        "Hotel Central",
        cidade.id,
        4,
    )

    resultado = hotel_repository.get_by_id(hotel.id)

    assert resultado is not None
    assert resultado.id == hotel.id
    assert resultado.nome == "Hotel Central"


def test_buscar_hotel_inexistente_repository(db_session):
    hotel_repository = HotelRepository(db_session)

    resultado = hotel_repository.get_by_id(
        UUID("00000000-0000-0000-0000-000000000000")
    )

    assert resultado is None


def test_buscar_comodidades_por_ids_repository(db_session):
    hotel_repository = HotelRepository(db_session)

    wifi = Comodidade(nome="Wi-Fi")
    piscina = Comodidade(nome="Piscina")

    db_session.add_all([wifi, piscina])
    db_session.commit()

    resultado = hotel_repository.get_comodidades_by_ids(
        [wifi.id, piscina.id]
    )

    assert len(resultado) == 2
    assert {item.nome for item in resultado} == {
        "Wi-Fi",
        "Piscina",
    }


def test_buscar_comodidades_com_lista_vazia_repository(db_session):
    hotel_repository = HotelRepository(db_session)

    resultado = hotel_repository.get_comodidades_by_ids([])

    assert resultado == []
