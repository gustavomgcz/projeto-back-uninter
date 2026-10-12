from datetime import datetime

from pydantic import BaseModel


class ConsentimentoRequest(BaseModel):
    consentiu: bool


class ConsentimentoResponse(BaseModel):
    consentiu: bool
    registradoEm: datetime


class MovimentoFidelidadeResponse(BaseModel):
    pedidoId: int
    pontos: int
    criadoEm: datetime


class SaldoResponse(BaseModel):
    consentiu: bool
    pontos: int
    historico: list[MovimentoFidelidadeResponse]
