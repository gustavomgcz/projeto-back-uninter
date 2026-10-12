from decimal import Decimal

import pytest

from app.domain.entities.fidelidade import calcular_pontos
from app.domain.entities.pedido import (
    ItemSolicitado, ProdutoDisponivel, validar_e_totalizar, validar_transicao,
)
from app.domain.exceptions import (
    EstoqueInsuficienteError, ProdutoNaoPertenceAUnidadeError, TransicaoStatusInvalidaError, ValidacaoError,
)
from app.domain.value_objects.status_pedido import StatusPedido


def prod(id=1, unidade=1, saldo=5, preco="10.00", ativo=True):
    return ProdutoDisponivel(id, f"p{id}", Decimal(preco), unidade, ativo, saldo)


def test_total_somado_com_itens_repetidos():
    total = validar_e_totalizar(1, [ItemSolicitado(1, 2), ItemSolicitado(1, 1)], {1: prod(preco="9.90")})
    assert total == Decimal("29.70")


def test_estoque_insuficiente_considera_soma_das_linhas():
    with pytest.raises(EstoqueInsuficienteError):
        validar_e_totalizar(1, [ItemSolicitado(1, 3), ItemSolicitado(1, 3)], {1: prod(saldo=5)})


def test_produto_fora_da_unidade_ou_inativo():
    with pytest.raises(ProdutoNaoPertenceAUnidadeError):
        validar_e_totalizar(1, [ItemSolicitado(1, 1)], {1: prod(unidade=2)})
    with pytest.raises(ProdutoNaoPertenceAUnidadeError):
        validar_e_totalizar(1, [ItemSolicitado(1, 1)], {1: prod(ativo=False)})


def test_pedido_vazio_ou_quantidade_invalida():
    with pytest.raises(ValidacaoError):
        validar_e_totalizar(1, [], {})
    with pytest.raises(ValidacaoError):
        validar_e_totalizar(1, [ItemSolicitado(1, 0)], {1: prod()})


@pytest.mark.parametrize("a,b", [
    (StatusPedido.AGUARDANDO_PAGAMENTO, StatusPedido.PAGO),
    (StatusPedido.PAGO, StatusPedido.EM_PREPARO),
    (StatusPedido.EM_PREPARO, StatusPedido.PRONTO),
    (StatusPedido.PRONTO, StatusPedido.ENTREGUE),
    (StatusPedido.PAGO, StatusPedido.CANCELADO),
])
def test_transicoes_validas(a, b):
    validar_transicao(a, b)


@pytest.mark.parametrize("a,b", [
    (StatusPedido.ENTREGUE, StatusPedido.EM_PREPARO),
    (StatusPedido.PRONTO, StatusPedido.CANCELADO),
    (StatusPedido.CANCELADO, StatusPedido.PAGO),
    (StatusPedido.PAGO, StatusPedido.PRONTO),
])
def test_transicoes_invalidas(a, b):
    with pytest.raises(TransicaoStatusInvalidaError):
        validar_transicao(a, b)


def test_pontos():
    assert calcular_pontos(Decimal("51.00")) == 51
    assert calcular_pontos(Decimal("9.99")) == 9
