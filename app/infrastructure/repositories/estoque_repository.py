from sqlalchemy import func, select

from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque
from app.infrastructure.db.models import Estoque, MovimentoEstoque
from app.infrastructure.repositories.base import BaseRepository


class EstoqueRepository(BaseRepository):
    def obter(self, produto_id: int, unidade_id: int, lock: bool = False) -> Estoque | None:
        stmt = select(Estoque).where(Estoque.produto_id == produto_id, Estoque.unidade_id == unidade_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def obter_varios_com_lock(self, produto_ids: list[int], unidade_id: int) -> dict[int, Estoque]:
        # trava em ordem de id pra não dar deadlock
        stmt = (
            select(Estoque)
            .where(Estoque.produto_id.in_(produto_ids), Estoque.unidade_id == unidade_id)
            .order_by(Estoque.produto_id)
            .with_for_update()
        )
        return {e.produto_id: e for e in self.db.scalars(stmt)}

    def registrar_movimento(self, estoque: Estoque, tipo: TipoMovimentoEstoque, quantidade: int,
                            novo_saldo: int, motivo: str | None = None,
                            pedido_id: int | None = None) -> MovimentoEstoque:
        estoque.saldo = novo_saldo
        mov = MovimentoEstoque(estoque_id=estoque.id, tipo=tipo, quantidade=quantidade,
                               motivo=motivo, pedido_id=pedido_id)
        self.db.add(mov)
        self.db.flush()
        return mov

    def listar(self, unidade_id: int, produto_id: int | None, page: int, limit: int) -> tuple[list[Estoque], int]:
        base = select(Estoque).where(Estoque.unidade_id == unidade_id)
        if produto_id is not None:
            base = base.where(Estoque.produto_id == produto_id)
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        itens = self.db.scalars(base.order_by(Estoque.id).offset((page - 1) * limit).limit(limit)).all()
        return list(itens), total or 0
