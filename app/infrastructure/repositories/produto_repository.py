from sqlalchemy import func, select

from app.infrastructure.db.models import Estoque, Produto
from app.infrastructure.repositories.base import BaseRepository


class ProdutoRepository(BaseRepository):
    def por_id(self, produto_id: int) -> Produto | None:
        return self.db.get(Produto, produto_id)

    def criar(self, **dados) -> Produto:
        produto = Produto(**dados)
        self.db.add(produto)
        self.db.flush()
        # todo produto novo já nasce com estoque zerado
        self.db.add(Estoque(produto_id=produto.id, unidade_id=produto.unidade_id, saldo=0))
        self.db.flush()
        return produto

    def cardapio(self, unidade_id: int, page: int, limit: int) -> tuple[list[tuple[Produto, int]], int]:
        base = (
            select(Produto, Estoque.saldo)
            .join(Estoque, (Estoque.produto_id == Produto.id) & (Estoque.unidade_id == Produto.unidade_id))
            .where(Produto.unidade_id == unidade_id, Produto.ativo.is_(True))
        )
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        rows = self.db.execute(
            base.order_by(Produto.id).offset((page - 1) * limit).limit(limit)
        ).all()
        return [(p, s) for p, s in rows], total or 0
