from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
    items: list[T]
    page: int
    limit: int
    total: int


class ErroPadrao(BaseModel):
    error: str
    message: str
    details: list[dict] = []
    timestamp: str
    path: str


_DESCRICOES = {400: "Requisição inválida", 401: "Não autenticado", 403: "Sem permissão",
               404: "Não encontrado", 409: "Conflito de regra de negócio", 422: "Validação"}


def erros(*codigos: int) -> dict:
    # mostra os erros possíveis no swagger
    return {c: {"model": ErroPadrao, "description": _DESCRICOES[c]} for c in sorted({*codigos, 422})}
