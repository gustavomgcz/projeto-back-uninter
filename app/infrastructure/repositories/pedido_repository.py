from sqlalchemy import func, select

from app.domain.entities.pagamento import ResultadoPagamento
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.status_pedido import StatusPedido
from app.infrastructure.db.models import HistoricoStatusPedido, ItemPedido, Pagamento, Pedido
from app.infrastructure.repositories.base import BaseRepository


class PedidoRepository(BaseRepository):
    def criar(self, cliente_id: int, unidade_id: int, canal: CanalPedido, total,
              itens: list[tuple[int, int, object]], criado_por: int | None) -> Pedido:
        pedido = Pedido(cliente_id=cliente_id, unidade_id=unidade_id, canal_pedido=canal,
                        status=StatusPedido.AGUARDANDO_PAGAMENTO, valor_total=total)
        pedido.itens = [ItemPedido(produto_id=p, quantidade=q, preco_unitario=preco) for p, q, preco in itens]
        pedido.historico = [HistoricoStatusPedido(status_anterior=None,
                                                  status_novo=StatusPedido.AGUARDANDO_PAGAMENTO,
                                                  alterado_por=criado_por)]
        self.db.add(pedido)
        self.db.flush()
        return pedido

    def por_id(self, pedido_id: int, lock: bool = False) -> Pedido | None:
        if lock:
            stmt = select(Pedido).where(Pedido.id == pedido_id).with_for_update()
            return self.db.scalar(stmt)
        return self.db.get(Pedido, pedido_id)

    def alterar_status(self, pedido: Pedido, novo: StatusPedido, alterado_por: int | None,
                       motivo: str | None = None) -> None:
        pedido.historico.append(HistoricoStatusPedido(status_anterior=pedido.status, status_novo=novo,
                                                      alterado_por=alterado_por))
        pedido.status = novo
        if motivo is not None:
            pedido.motivo_cancelamento = motivo
        self.db.flush()

    def registrar_pagamento(self, pedido: Pedido, resultado: ResultadoPagamento, payload: dict) -> Pagamento:
        pagamento = Pagamento(pedido_id=pedido.id, resultado=resultado, payload_mock=payload)
        self.db.add(pagamento)
        pedido.pagamento = pagamento
        self.db.flush()
        return pagamento

    def listar(self, *, cliente_id: int | None, unidade_id: int | None, canal: CanalPedido | None,
               status: StatusPedido | None, page: int, limit: int) -> tuple[list[Pedido], int]:
        base = select(Pedido)
        if cliente_id is not None:
            base = base.where(Pedido.cliente_id == cliente_id)
        if unidade_id is not None:
            base = base.where(Pedido.unidade_id == unidade_id)
        if canal is not None:
            base = base.where(Pedido.canal_pedido == canal)
        if status is not None:
            base = base.where(Pedido.status == status)
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        itens = self.db.scalars(
            base.order_by(Pedido.id.desc()).offset((page - 1) * limit).limit(limit)
        ).all()
        return list(itens), total or 0
