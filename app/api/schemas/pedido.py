from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.entities.pagamento import ResultadoPagamento
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.status_pedido import StatusPedido


class ItemRequest(BaseModel):
    produtoId: int
    quantidade: int = Field(gt=0)


class PedidoCreate(BaseModel):
    unidadeId: int
    canalPedido: CanalPedido
    itens: list[ItemRequest] = Field(min_length=1)
    clienteId: int | None = Field(default=None, description="Obrigatório apenas quando um ATENDENTE cria o pedido")


class ItemResponse(BaseModel):
    produtoId: int
    quantidade: int
    precoUnitario: Decimal


class HistoricoResponse(BaseModel):
    statusAnterior: StatusPedido | None
    statusNovo: StatusPedido
    alteradoPor: int | None
    criadoEm: datetime


class PedidoResponse(BaseModel):
    pedidoId: int
    clienteId: int
    unidadeId: int
    status: StatusPedido
    canalPedido: CanalPedido
    total: Decimal
    itens: list[ItemResponse]
    motivoCancelamento: str | None = None
    historico: list[HistoricoResponse] = []
    createdAt: datetime


class PagamentoRequest(BaseModel):
    formaPagamento: str = Field(default="MOCK", pattern="^(PIX|CARTAO|MOCK)$")
    forcarResultado: ResultadoPagamento | None = None


class PagamentoResponse(BaseModel):
    pedidoId: int
    resultado: ResultadoPagamento
    status: StatusPedido
    respondidoEm: datetime


class StatusUpdate(BaseModel):
    novoStatus: StatusPedido
    motivo: str | None = Field(default=None, max_length=255)


def pedido_response(p) -> PedidoResponse:
    return PedidoResponse(
        pedidoId=p.id, clienteId=p.cliente_id, unidadeId=p.unidade_id, status=p.status,
        canalPedido=p.canal_pedido, total=p.valor_total,
        itens=[ItemResponse(produtoId=i.produto_id, quantidade=i.quantidade, precoUnitario=i.preco_unitario)
               for i in p.itens],
        motivoCancelamento=p.motivo_cancelamento,
        historico=[HistoricoResponse(statusAnterior=h.status_anterior, statusNovo=h.status_novo,
                                     alteradoPor=h.alterado_por, criadoEm=h.criado_em) for h in p.historico],
        createdAt=p.criado_em,
    )
