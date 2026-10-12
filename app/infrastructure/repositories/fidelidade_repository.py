from sqlalchemy import select

from app.infrastructure.db.models import ConsentimentoFidelidade, MovimentoFidelidade, SaldoFidelidade
from app.infrastructure.repositories.base import BaseRepository


class FidelidadeRepository(BaseRepository):
    def consentimento(self, cliente_id: int) -> ConsentimentoFidelidade | None:
        return self.db.scalar(select(ConsentimentoFidelidade).where(ConsentimentoFidelidade.cliente_id == cliente_id))

    def registrar_consentimento(self, cliente_id: int, consentiu: bool) -> ConsentimentoFidelidade:
        c = self.consentimento(cliente_id)
        if c is None:
            c = ConsentimentoFidelidade(cliente_id=cliente_id, consentiu=consentiu)
            self.db.add(c)
        else:
            c.consentiu = consentiu
        self.db.flush()
        return c

    def saldo(self, cliente_id: int, lock: bool = False) -> SaldoFidelidade | None:
        stmt = select(SaldoFidelidade).where(SaldoFidelidade.cliente_id == cliente_id)
        if lock:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def creditar(self, cliente_id: int, pedido_id: int, pontos: int) -> None:
        saldo = self.saldo(cliente_id, lock=True)
        if saldo is None:
            saldo = SaldoFidelidade(cliente_id=cliente_id, pontos=0)
            self.db.add(saldo)
        saldo.pontos += pontos
        self.db.add(MovimentoFidelidade(cliente_id=cliente_id, pedido_id=pedido_id, pontos=pontos))
        self.db.flush()

    def historico(self, cliente_id: int) -> list[MovimentoFidelidade]:
        return list(self.db.scalars(
            select(MovimentoFidelidade).where(MovimentoFidelidade.cliente_id == cliente_id)
            .order_by(MovimentoFidelidade.id.desc())
        ))
