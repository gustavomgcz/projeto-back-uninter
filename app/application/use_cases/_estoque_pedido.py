from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque


def devolver_estoque(estoques, pedido, motivo: str) -> None:
    for item in sorted(pedido.itens, key=lambda i: i.produto_id):
        est = estoques.obter(item.produto_id, pedido.unidade_id, lock=True)
        if est is not None:
            estoques.registrar_movimento(est, TipoMovimentoEstoque.ENTRADA, item.quantidade,
                                         est.saldo + item.quantidade, motivo=motivo, pedido_id=pedido.id)
