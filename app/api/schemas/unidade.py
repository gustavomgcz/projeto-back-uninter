from pydantic import BaseModel


class UnidadeResponse(BaseModel):
    id: int
    nome: str
    cidade: str | None
    tipoOperacao: str
