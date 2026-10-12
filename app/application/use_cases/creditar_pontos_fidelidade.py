from app.domain.entities.fidelidade import calcular_pontos
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository


class CreditarPontosFidelidade:

    def __init__(self, fidelidade: FidelidadeRepository):
        self.fidelidade = fidelidade

    def executar(self, pedido) -> int:
        consentimento = self.fidelidade.consentimento(pedido.cliente_id)
        if consentimento is None or not consentimento.consentiu:
            return 0
        pontos = calcular_pontos(pedido.valor_total)
        if pontos > 0:
            self.fidelidade.creditar(pedido.cliente_id, pedido.id, pontos)
        return pontos
