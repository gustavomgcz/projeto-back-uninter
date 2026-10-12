from app.domain.exceptions import SaidaMaiorQueSaldoError, ValidacaoError
from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque


def novo_saldo(saldo: int, tipo: TipoMovimentoEstoque, quantidade: int) -> int:
    if quantidade <= 0:
        raise ValidacaoError("Quantidade deve ser maior que zero")
    if tipo == TipoMovimentoEstoque.ENTRADA:
        return saldo + quantidade
    if quantidade > saldo:
        raise SaidaMaiorQueSaldoError(
            f"Saída ({quantidade}) maior que o saldo atual ({saldo})"
        )
    return saldo - quantidade
