from dataclasses import dataclass
from decimal import Decimal

from app.domain.exceptions import (
    EstoqueInsuficienteError,
    ProdutoNaoPertenceAUnidadeError,
    TransicaoStatusInvalidaError,
    ValidacaoError,
)
from app.domain.value_objects.status_pedido import StatusPedido, transicao_valida


@dataclass(frozen=True)
class ItemSolicitado:
    produto_id: int
    quantidade: int


@dataclass(frozen=True)
class ProdutoDisponivel:
    id: int
    nome: str
    preco: Decimal
    unidade_id: int
    ativo: bool
    saldo: int


def validar_e_totalizar(
    unidade_id: int,
    itens: list[ItemSolicitado],
    produtos: dict[int, ProdutoDisponivel],
) -> Decimal:
    # se um item falhar o pedido todo é rejeitado
    if not itens:
        raise ValidacaoError("O pedido precisa ter ao menos um item")

    # mesmo produto em várias linhas conta junto
    por_produto: dict[int, int] = {}
    for item in itens:
        if item.quantidade <= 0:
            raise ValidacaoError("Quantidade deve ser maior que zero")
        por_produto[item.produto_id] = por_produto.get(item.produto_id, 0) + item.quantidade

    total = Decimal("0")
    for produto_id, quantidade in por_produto.items():
        produto = produtos[produto_id]
        if produto.unidade_id != unidade_id or not produto.ativo:
            raise ProdutoNaoPertenceAUnidadeError(
                f"Produto {produto_id} não pertence à unidade {unidade_id} ou está inativo",
                [{"field": "itens.produtoId", "issue": str(produto_id)}],
            )
        if quantidade > produto.saldo:
            raise EstoqueInsuficienteError(
                f"Estoque insuficiente para '{produto.nome}' "
                f"(disponível: {produto.saldo}, solicitado: {quantidade})",
                [{"field": "itens.quantidade", "issue": str(produto_id)}],
            )
        total += produto.preco * quantidade
    return total


def validar_transicao(atual: StatusPedido, novo: StatusPedido) -> None:
    if not transicao_valida(atual, novo):
        raise TransicaoStatusInvalidaError(
            f"Transição de {atual.value} para {novo.value} não é permitida"
        )
