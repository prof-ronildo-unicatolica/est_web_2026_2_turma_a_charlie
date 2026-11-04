from decimal import Decimal

import pytest

from app.services.reserva_service import (
    aplicar_desconto_nao_reembolsavel,
    aplicar_tarifa_temporada,
    aplicar_taxa_early_late,
    calcular_diarias,
    calcular_servicos_adicionais,
    calcular_total,
    calcular_valor_criancas,
)


def test_calcular_diarias():
    resultado = calcular_diarias(
        preco_diaria=Decimal("200.00"),
        quantidade_diarias=3,
    )

    assert resultado == Decimal("600.00")


def test_aplicar_tarifa_temporada():
    resultado = aplicar_tarifa_temporada(
        valor=Decimal("600.00"),
        percentual=Decimal("20.00"),
    )

    assert resultado == Decimal("720.00")


def test_calcular_valor_criancas():
    resultado = calcular_valor_criancas(
        valor_diaria=Decimal("200.00"),
        idades=[3, 8, 12, 15],
    )

    assert resultado == Decimal("200.00")


def test_aplicar_taxa_early_late():
    resultado = aplicar_taxa_early_late(
        valor=Decimal("600.00"),
        early_checkin=True,
        late_checkout=False,
    )

    assert resultado == Decimal("780.00")


def test_calcular_servicos_adicionais():
    resultado = calcular_servicos_adicionais(
        precos=[
            Decimal("50.00"),
            Decimal("30.00"),
            Decimal("20.00"),
        ],
    )

    assert resultado == Decimal("100.00")


def test_aplicar_desconto_nao_reembolsavel():
    resultado = aplicar_desconto_nao_reembolsavel(
        valor=Decimal("1000.00"),
        nao_reembolsavel=True,
    )

    assert resultado == Decimal("900.00")


def test_calcular_total():
    resultado = calcular_total(
        preco_diaria=Decimal("200.00"),
        quantidade_diarias=3,
        percentual_temporada=Decimal("20.00"),
        idades_criancas=[8],
        early_checkin=True,
        late_checkout=False,
        precos_servicos=[
            Decimal("50.00"),
        ],
        nao_reembolsavel=True,
    )

    assert resultado == Decimal("1004.40")

@pytest.mark.parametrize(
    ("preco_diaria", "quantidade_diarias", "esperado"),
    [
        (Decimal("200.00"), 0, Decimal("0.00")),
        (Decimal("99.99"), 3, Decimal("299.97")),
    ],
)
def test_calcular_diarias_casos_adicionais(
    preco_diaria,
    quantidade_diarias,
    esperado,
):
    resultado = calcular_diarias(preco_diaria, quantidade_diarias)

    assert resultado == esperado


def test_aplicar_tarifa_temporada_sem_aumento():
    resultado = aplicar_tarifa_temporada(
        valor=Decimal("600.00"),
        percentual=Decimal("0.00"),
    )

    assert resultado == Decimal("600.00")


@pytest.mark.parametrize(
    ("idades", "esperado"),
    [
        ([], Decimal("0.00")),
        ([5], Decimal("0.00")),
        ([6], Decimal("100.00")),
        ([12], Decimal("100.00")),
        ([13], Decimal("0.00")),
    ],
)
def test_calcular_valor_criancas_faixas_etarias(idades, esperado):
    resultado = calcular_valor_criancas(
        valor_diaria=Decimal("200.00"),
        idades=idades,
    )

    assert resultado == esperado


@pytest.mark.parametrize(
    ("early_checkin", "late_checkout", "esperado"),
    [
        (False, False, Decimal("600.00")),
        (False, True, Decimal("780.00")),
        (True, True, Decimal("960.00")),
    ],
)
def test_aplicar_taxa_early_late_combinacoes(
    early_checkin,
    late_checkout,
    esperado,
):
    resultado = aplicar_taxa_early_late(
        valor=Decimal("600.00"),
        early_checkin=early_checkin,
        late_checkout=late_checkout,
    )

    assert resultado == esperado


def test_calcular_servicos_adicionais_lista_vazia():
    resultado = calcular_servicos_adicionais(precos=[])

    assert resultado == Decimal("0.00")


def test_aplicar_desconto_nao_reembolsavel_desativado():
    resultado = aplicar_desconto_nao_reembolsavel(
        valor=Decimal("1000.00"),
        nao_reembolsavel=False,
    )

    assert resultado == Decimal("1000.00")


def test_calcular_total_com_valores_padrao():
    resultado = calcular_total(
        preco_diaria=Decimal("150.00"),
        quantidade_diarias=2,
    )

    assert resultado == Decimal("300.00")