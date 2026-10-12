from enum import Enum


class PerfilUsuario(str, Enum):
    CLIENTE = "CLIENTE"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    GERENTE_ADMIN = "GERENTE_ADMIN"


PERFIS_OPERACIONAIS = {
    PerfilUsuario.ATENDENTE,
    PerfilUsuario.COZINHA,
    PerfilUsuario.GERENTE_ADMIN,
}
