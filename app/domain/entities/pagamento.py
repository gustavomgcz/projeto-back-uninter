from enum import Enum


class ResultadoPagamento(str, Enum):
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"
