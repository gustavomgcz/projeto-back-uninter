# simulador de pagamento, não cobra nada de verdade
import hashlib

from app.domain.entities.pagamento import ResultadoPagamento


def processar(pedido_id: int, valor: float, forma_pagamento: str,
              forcar_resultado: ResultadoPagamento | None = None) -> tuple[ResultadoPagamento, dict]:
    # sem forcarResultado: hash do id par aprova, ímpar recusa
    if forcar_resultado is not None:
        resultado = forcar_resultado
    else:
        digest = int(hashlib.sha256(str(pedido_id).encode()).hexdigest(), 16)
        resultado = ResultadoPagamento.APROVADO if digest % 2 == 0 else ResultadoPagamento.RECUSADO
    payload = {
        "request": {"pedidoId": pedido_id, "valor": valor, "formaPagamento": forma_pagamento},
        "response": {"status": resultado.value, "gateway": "MOCK"},
    }
    return resultado, payload
