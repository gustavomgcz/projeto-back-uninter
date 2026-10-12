from app.domain.exceptions import ValidacaoError
from app.domain.value_objects.perfil_usuario import PERFIS_OPERACIONAIS, PerfilUsuario


def validar_vinculo_unidade(perfil: PerfilUsuario, unidade_id: int | None) -> None:
    if perfil in PERFIS_OPERACIONAIS and unidade_id is None:
        raise ValidacaoError(f"Perfil {perfil.value} exige unidadeId")
    if perfil == PerfilUsuario.CLIENTE and unidade_id is not None:
        raise ValidacaoError("CLIENTE não deve ter unidadeId")
