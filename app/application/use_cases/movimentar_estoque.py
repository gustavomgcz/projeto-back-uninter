from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.domain.entities.estoque import novo_saldo
from app.domain.exceptions import NaoEncontradoError, ValidacaoError
from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque
from app.infrastructure.repositories.estoque_repository import EstoqueRepository


class MovimentarEstoque:
    def __init__(self, estoques: EstoqueRepository):
        self.estoques = estoques

    def executar(self, ator, *, produto_id: int, unidade_id: int, tipo: TipoMovimentoEstoque,
                 quantidade: int, motivo: str | None):
        exigir_mesma_unidade(ator, unidade_id)
        if tipo == TipoMovimentoEstoque.SAIDA and not motivo:
            raise ValidacaoError("Motivo é obrigatório para saída manual",
                                 [{"field": "motivo", "issue": "obrigatório para SAIDA"}])
        estoque = self.estoques.obter(produto_id, unidade_id, lock=True)
        if estoque is None:
            raise NaoEncontradoError("Estoque não encontrado para o produto/unidade")
        try:
            saldo = novo_saldo(estoque.saldo, tipo, quantidade)
            mov = self.estoques.registrar_movimento(estoque, tipo, quantidade, saldo, motivo)
            self.estoques.commit()
        except Exception:
            self.estoques.rollback()
            raise
        return mov, estoque


class ConsultarEstoque:
    def __init__(self, estoques: EstoqueRepository):
        self.estoques = estoques

    def executar(self, ator, unidade_id: int, produto_id: int | None, page: int, limit: int):
        exigir_mesma_unidade(ator, unidade_id)
        return self.estoques.listar(unidade_id, produto_id, page, limit)
