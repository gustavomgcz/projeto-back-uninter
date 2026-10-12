from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque


class MovimentoEstoqueRequest(BaseModel):
    produtoId: int
    unidadeId: int
    tipo: TipoMovimentoEstoque
    quantidade: int = Field(gt=0)
    motivo: str | None = Field(default=None, max_length=255)


class EstoqueResponse(BaseModel):
    produtoId: int
    unidadeId: int
    saldo: int
    atualizadoEm: datetime


class MovimentoEstoqueResponse(BaseModel):
    movimentoId: int
    tipo: TipoMovimentoEstoque
    quantidade: int
    saldoAtual: int
