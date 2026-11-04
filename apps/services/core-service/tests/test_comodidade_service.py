from unittest.mock import Mock

import app.services.comodidade_service as comodidade_module
from app.services.comodidade_service import ComodidadeService


def criar_service(monkeypatch):
    repository = Mock()

    monkeypatch.setattr(
        comodidade_module,
        "ComodidadeRepository",
        lambda db: repository,
    )

    service = ComodidadeService(db=Mock())

    return service, repository


def test_create_comodidade(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidade = Mock()
    repository.create.return_value = comodidade

    resultado = service.create("Wi-Fi")

    repository.create.assert_called_once_with("Wi-Fi")
    assert resultado is comodidade


def test_list_comodidades(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidades = [Mock(), Mock()]
    repository.list.return_value = comodidades

    resultado = service.list()

    repository.list.assert_called_once_with()
    assert resultado == comodidades


def test_get_by_id(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidade = Mock()
    repository.get_by_id.return_value = comodidade

    resultado = service.get_by_id(1)

    repository.get_by_id.assert_called_once_with(1)
    assert resultado is comodidade


def test_get_by_nome(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidade = Mock()
    repository.get_by_nome.return_value = comodidade

    resultado = service.get_by_nome("Wi-Fi")

    repository.get_by_nome.assert_called_once_with("Wi-Fi")
    assert resultado is comodidade


def test_update_comodidade(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidade = Mock()
    atualizada = Mock()
    repository.update.return_value = atualizada

    resultado = service.update(comodidade, "Piscina")

    repository.update.assert_called_once_with(comodidade, "Piscina")
    assert resultado is atualizada


def test_delete_comodidade(monkeypatch):
    service, repository = criar_service(monkeypatch)
    comodidade = Mock()

    resultado = service.delete(comodidade)

    repository.delete.assert_called_once_with(comodidade)
    assert resultado is None