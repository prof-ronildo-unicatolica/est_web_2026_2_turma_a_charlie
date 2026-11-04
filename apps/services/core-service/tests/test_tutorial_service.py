import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import app.services.tutorial_service as tutorial_module
from app.services.tutorial_service import TutorialService


def criar_service(monkeypatch):
    repository = Mock()

    publisher = AsyncMock()

    monkeypatch.setattr(
        tutorial_module,
        "TutorialRepository",
        lambda db: repository,
    )

    monkeypatch.setattr(
        tutorial_module,
        "publish_event",
        publisher,
    )

    service = TutorialService(db=Mock())

    return service, repository, publisher


def test_get_sobre_data_sem_professores_e_stacks(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)

    repository.get_professor_with_details.return_value = []
    repository.get_stacks_with_tecnologias.return_value = []

    resultado = service.get_sobre_data()

    assert resultado["equipe"] == "Alpha"
    assert resultado["ano"] == 2026
    assert resultado["semestre"] == 2
    assert resultado["professor"] is None
    assert resultado["disciplinas"] == []
    assert resultado["stacks"] == []


def test_get_sobre_data_professor_sem_detalhes(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)

    professor = SimpleNamespace(
        nome="Maria",
        email="maria@hotel.com",
        detalhe=None,
        disciplinas=[],
    )

    repository.get_professor_with_details.return_value = [professor]
    repository.get_stacks_with_tecnologias.return_value = []

    resultado = service.get_sobre_data()

    assert resultado["professor"]["nome"] == "Maria"
    assert resultado["professor"]["sala"] == ""
    assert resultado["professor"]["biografia"] == ""
    assert resultado["professor"]["biografia_mapa"] is None
    assert resultado["disciplinas"] == []


def test_get_sobre_data_com_professor_disciplinas_e_stacks(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)

    detalhe = SimpleNamespace(
        sala="Sala 10",
        biografia="Professor da equipe",
        biografia_mapa="mapa-exemplo",
    )

    tecnologia_disciplina = SimpleNamespace(nome="Python")

    disciplina = SimpleNamespace(
        nome="Desenvolvimento Web",
        ano=2026,
        semestre=2,
        tecnologias=[tecnologia_disciplina],
    )

    professor = SimpleNamespace(
        nome="Carlos",
        email="carlos@hotel.com",
        detalhe=detalhe,
        disciplinas=[disciplina],
    )

    linguagem = SimpleNamespace(nome="Python")

    tecnologia_stack = SimpleNamespace(
        nome="Backend",
        linguagens=[linguagem],
    )

    stack = SimpleNamespace(
        nome="Desenvolvimento",
        tecnologias=[tecnologia_stack],
    )

    repository.get_professor_with_details.return_value = [professor]
    repository.get_stacks_with_tecnologias.return_value = [stack]

    resultado = service.get_sobre_data()

    assert resultado["professor"]["sala"] == "Sala 10"
    assert resultado["professor"]["biografia"] == "Professor da equipe"
    assert resultado["professor"]["biografia_mapa"] == "mapa-exemplo"

    assert resultado["disciplinas"] == [
        {
            "nome": "Desenvolvimento Web",
            "ano": 2026,
            "semestre": 2,
            "tecnologias": ["Python"],
        }
    ]

    assert resultado["stacks"] == [
        {
            "nome": "Desenvolvimento",
            "tecnologias": [
                {
                    "nome": "Backend",
                    "linguagens": ["Python"],
                }
            ],
        }
    ]


def test_get_professor_by_id(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)

    professor = Mock()
    repository.get_professor_by_id.return_value = professor

    resultado = service.get_professor_by_id("professor-123")

    repository.get_professor_by_id.assert_called_once_with(
        "professor-123"
    )
    assert resultado is professor


def test_create_professor(monkeypatch):
    service, repository, _ = criar_service(monkeypatch)

    payload = SimpleNamespace(
        nome="Carlos",
        email="carlos@hotel.com",
        sala="Sala 10",
        biografia="Professor",
        biografia_mapa="mapa",
    )

    professor = Mock()
    repository.create_professor.return_value = professor

    resultado = service.create_professor(payload)

    repository.create_professor.assert_called_once_with(
        nome="Carlos",
        email="carlos@hotel.com",
        sala="Sala 10",
        biografia="Professor",
        biografia_mapa="mapa",
    )

    assert resultado is professor


def test_create_disciplina_publica_evento(monkeypatch):
    service, repository, publisher = criar_service(monkeypatch)

    payload = SimpleNamespace(
        nome="Desenvolvimento Web",
        ano=2026,
        semestre=2,
        professor_id="professor-123",
    )

    disciplina = SimpleNamespace(
        id="disciplina-123",
        nome="Desenvolvimento Web",
        ano=2026,
        semestre=2,
        professor_id="professor-123",
    )

    repository.create_disciplina.return_value = disciplina

    resultado = asyncio.run(service.create_disciplina(payload))

    repository.create_disciplina.assert_called_once_with(
        nome="Desenvolvimento Web",
        ano=2026,
        semestre=2,
        professor_id="professor-123",
    )

    publisher.assert_awaited_once_with(
        "audit.logs",
        {
            "evento": "disciplina.criada",
            "disciplina_id": "disciplina-123",
            "nome": "Desenvolvimento Web",
            "ano": 2026,
            "semestre": 2,
            "professor_id": "professor-123",
        },
    )

    assert resultado is disciplina