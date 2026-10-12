from decimal import Decimal

from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    preco: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    unidadeId: int


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: Decimal
    unidadeId: int
    ativo: bool
    saldo: int | None = None
