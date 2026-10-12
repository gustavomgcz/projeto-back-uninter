from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.application.use_cases._estoque_pedido import devolver_estoque
from app.application.use_cases.creditar_pontos_fidelidade import CreditarPontosFidelidade
from app.domain.entities.pagamento import ResultadoPagamento
from app.domain.exceptions import (
    AcessoNegadoError, FalhaPagamentoMockError, NaoEncontradoError,
    PagamentoJaProcessadoError, PedidoNaoAguardaPagamentoError,
)
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.domain.value_objects.status_pedido import StatusPedido
from app.infrastructure.payment import mock_gateway
from app.infrastructure.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.repositories.pedido_repository import PedidoRepository


class SolicitarPagamentoMock:
    def __init__(self, pedidos: PedidoRepository, estoques: EstoqueRepository,
                 creditar: CreditarPontosFidelidade, gateway=mock_gateway):
        self.pedidos = pedidos
        self.estoques = estoques
        self.creditar = creditar
        self.gateway = gateway

    def executar(self, ator, pedido_id: int, forma_pagamento: str,
                 forcar_resultado: ResultadoPagamento | None):
        # trava o pedido, assim dois pagamentos ao mesmo tempo não passam juntos
        pedido = self.pedidos.por_id(pedido_id, lock=True)
        try:
            if pedido is None:
                raise NaoEncontradoError("Pedido não encontrado")
            if ator.perfil == PerfilUsuario.CLIENTE:
                if pedido.cliente_id != ator.id:
                    raise AcessoNegadoError("Pedido de outro cliente")
            elif ator.perfil == PerfilUsuario.ATENDENTE:
                exigir_mesma_unidade(ator, pedido.unidade_id)
            else:
                raise AcessoNegadoError("Perfil sem permissão para solicitar pagamento")

            if pedido.pagamento is not None:
                raise PagamentoJaProcessadoError("Pedido já possui resultado de pagamento")
            if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
                raise PedidoNaoAguardaPagamentoError(
                    f"Pedido está em {pedido.status.value}, não aguarda pagamento")

            try:
                resultado, payload = self.gateway.processar(
                    pedido.id, float(pedido.valor_total), forma_pagamento, forcar_resultado)
            except Exception as exc:  # falhou: o pedido continua aguardando pagamento
                raise FalhaPagamentoMockError("Falha ao processar pagamento; tente novamente") from exc

            self.pedidos.registrar_pagamento(pedido, resultado, payload)
            if resultado == ResultadoPagamento.APROVADO:
                self.pedidos.alterar_status(pedido, StatusPedido.PAGO, None)
                self.creditar.executar(pedido)
            else:
                self.pedidos.alterar_status(pedido, StatusPedido.PAGAMENTO_RECUSADO, None)
                devolver_estoque(self.estoques, pedido, "Estorno - pagamento recusado")
            self.pedidos.commit()
        except Exception:
            self.pedidos.rollback()
            raise
        return pedido
