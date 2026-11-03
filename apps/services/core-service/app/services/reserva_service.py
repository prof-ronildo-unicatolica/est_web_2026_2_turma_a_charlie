from decimal import Decimal


def calcular_diarias(
    preco_diaria: Decimal,
    quantidade_diarias: int,
) -> Decimal:
    """Calcula o valor base das diárias."""

    return preco_diaria * quantidade_diarias


def aplicar_tarifa_temporada(
    valor: Decimal,
    percentual: Decimal,
) -> Decimal:
    """Aplica o percentual da tarifa de temporada."""

    aumento = valor * percentual / Decimal("100")

    return valor + aumento


def calcular_valor_criancas(
    valor_diaria: Decimal,
    idades: list[int],
) -> Decimal:
    """Calcula o valor das diárias das crianças."""

    total = Decimal("0.00")

    for idade in idades:
        if idade <= 5:
            continue

        if idade <= 12:
            total += valor_diaria * Decimal("0.50")

    return total


def aplicar_taxa_early_late(
    valor: Decimal,
    early_checkin: bool = False,
    late_checkout: bool = False,
) -> Decimal:
    """Aplica 30% para early check-in e 30% para late check-out."""

    quantidade_taxas = int(early_checkin) + int(late_checkout)

    aumento = valor * Decimal("0.30") * quantidade_taxas

    return valor + aumento


def calcular_servicos_adicionais(
    precos: list[Decimal],
) -> Decimal:
    """Calcula o total dos serviços adicionais."""

    return sum(precos, Decimal("0.00"))


def aplicar_desconto_nao_reembolsavel(
    valor: Decimal,
    nao_reembolsavel: bool = False,
) -> Decimal:
    """Aplica desconto de 10% para reserva não reembolsável."""

    if not nao_reembolsavel:
        return valor

    desconto = valor * Decimal("0.10")

    return valor - desconto


def calcular_total(
    preco_diaria: Decimal,
    quantidade_diarias: int,
    percentual_temporada: Decimal = Decimal("0.00"),
    idades_criancas: list[int] | None = None,
    early_checkin: bool = False,
    late_checkout: bool = False,
    precos_servicos: list[Decimal] | None = None,
    nao_reembolsavel: bool = False,
) -> Decimal:
    """Calcula o valor total da reserva."""

    if idades_criancas is None:
        idades_criancas = []

    if precos_servicos is None:
        precos_servicos = []

    valor_diarias = calcular_diarias(
        preco_diaria,
        quantidade_diarias,
    )

    valor_temporada = aplicar_tarifa_temporada(
        valor_diarias,
        percentual_temporada,
    )

    valor_criancas = calcular_valor_criancas(
        preco_diaria,
        idades_criancas,
    )

    total = valor_temporada + valor_criancas

    total = aplicar_taxa_early_late(
        total,
        early_checkin,
        late_checkout,
    )

    total += calcular_servicos_adicionais(precos_servicos)

    total = aplicar_desconto_nao_reembolsavel(
        total,
        nao_reembolsavel,
    )

    return total