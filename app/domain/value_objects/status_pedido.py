from enum import Enum


class StatusPedido(str, Enum):
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    PAGO = "PAGO"
    PAGAMENTO_RECUSADO = "PAGAMENTO_RECUSADO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


TRANSICOES_VALIDAS: dict[StatusPedido, set[StatusPedido]] = {
    StatusPedido.AGUARDANDO_PAGAMENTO: {
        StatusPedido.PAGO,
        StatusPedido.PAGAMENTO_RECUSADO,
        StatusPedido.CANCELADO,
    },
    StatusPedido.PAGO: {StatusPedido.EM_PREPARO, StatusPedido.CANCELADO},
    StatusPedido.EM_PREPARO: {StatusPedido.PRONTO},
    StatusPedido.PRONTO: {StatusPedido.ENTREGUE},
    StatusPedido.PAGAMENTO_RECUSADO: set(),
    StatusPedido.ENTREGUE: set(),
    StatusPedido.CANCELADO: set(),
}


def transicao_valida(atual: StatusPedido, novo: StatusPedido) -> bool:
    return novo in TRANSICOES_VALIDAS[atual]
