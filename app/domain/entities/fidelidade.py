from decimal import Decimal, ROUND_DOWN

PONTOS_POR_REAL = 1


def calcular_pontos(valor_pago: Decimal) -> int:
    # 1 ponto por real inteiro
    return int(valor_pago.to_integral_value(rounding=ROUND_DOWN)) * PONTOS_POR_REAL
