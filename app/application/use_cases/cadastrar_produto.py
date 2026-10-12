from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.domain.exceptions import NaoEncontradoError
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository


class CadastrarProduto:
    def __init__(self, unidades: UnidadeRepository, produtos: ProdutoRepository):
        self.unidades = unidades
        self.produtos = produtos

    def executar(self, ator, *, nome: str, descricao: str | None, preco, unidade_id: int):
        if self.unidades.por_id(unidade_id) is None:
            raise NaoEncontradoError("Unidade não encontrada")
        exigir_mesma_unidade(ator, unidade_id)
        produto = self.produtos.criar(nome=nome, descricao=descricao, preco=preco, unidade_id=unidade_id)
        self.produtos.commit()
        return produto
