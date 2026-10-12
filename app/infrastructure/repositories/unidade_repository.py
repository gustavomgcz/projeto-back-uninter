from sqlalchemy import func, select

from app.infrastructure.db.models import Unidade
from app.infrastructure.repositories.base import BaseRepository


class UnidadeRepository(BaseRepository):
    def por_id(self, unidade_id: int) -> Unidade | None:
        return self.db.get(Unidade, unidade_id)

    def listar_ativas(self, page: int, limit: int) -> tuple[list[Unidade], int]:
        base = select(Unidade).where(Unidade.ativa.is_(True))
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        itens = self.db.scalars(
            base.order_by(Unidade.id).offset((page - 1) * limit).limit(limit)
        ).all()
        return list(itens), total or 0
