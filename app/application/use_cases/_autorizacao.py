from app.domain.exceptions import AcessoNegadoError


def exigir_mesma_unidade(ator, unidade_id: int) -> None:
    if ator.unidade_id != unidade_id:
        raise AcessoNegadoError("Acesso negado: recurso de outra unidade")
