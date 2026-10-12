from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository


class ConsultarSaldoFidelidade:
    def __init__(self, fidelidade: FidelidadeRepository):
        self.fidelidade = fidelidade

    def executar(self, cliente_id: int):
        # a rota não recebe id, só dá pra ver o próprio saldo
        consentimento = self.fidelidade.consentimento(cliente_id)
        saldo = self.fidelidade.saldo(cliente_id)
        return (
            bool(consentimento and consentimento.consentiu),
            saldo.pontos if saldo else 0,
            self.fidelidade.historico(cliente_id),
        )
