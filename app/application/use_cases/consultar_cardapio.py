from app.domain.exceptions import NaoEncontradoError
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository


class ConsultarCardapio:
    def __init__(self, unidades: UnidadeRepository, produtos: ProdutoRepository):
        self.unidades = unidades
        self.produtos = produtos

    def executar(self, unidade_id: int, page: int, limit: int):
        if self.unidades.por_id(unidade_id) is None:
            raise NaoEncontradoError("Unidade não encontrada")
        return self.produtos.cardapio(unidade_id, page, limit)
