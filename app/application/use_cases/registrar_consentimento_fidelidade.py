from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository


class RegistrarConsentimentoFidelidade:
    def __init__(self, fidelidade: FidelidadeRepository):
        self.fidelidade = fidelidade

    def executar(self, cliente_id: int, consentiu: bool):
        c = self.fidelidade.registrar_consentimento(cliente_id, consentiu)
        self.fidelidade.commit()
        return c
