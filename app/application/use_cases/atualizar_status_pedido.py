from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.application.use_cases._estoque_pedido import devolver_estoque
from app.domain.entities.pedido import validar_transicao
from app.domain.exceptions import AcessoNegadoError, NaoEncontradoError, ValidacaoError
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.domain.value_objects.status_pedido import StatusPedido
from app.infrastructure.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.repositories.pedido_repository import PedidoRepository

_AVANCO = {StatusPedido.EM_PREPARO, StatusPedido.PRONTO, StatusPedido.ENTREGUE}
_PERFIS_AVANCO = {PerfilUsuario.COZINHA, PerfilUsuario.ATENDENTE, PerfilUsuario.GERENTE_ADMIN}


class AtualizarStatusPedido:
    def __init__(self, pedidos: PedidoRepository, estoques: EstoqueRepository):
        self.pedidos = pedidos
        self.estoques = estoques

    def executar(self, ator, pedido_id: int, novo: StatusPedido, motivo: str | None):
        pedido = self.pedidos.por_id(pedido_id, lock=True)
        try:
            if pedido is None:
                raise NaoEncontradoError("Pedido não encontrado")

            if novo in _AVANCO:
                if ator.perfil not in _PERFIS_AVANCO:
                    raise AcessoNegadoError("Perfil sem permissão para avançar status")
                exigir_mesma_unidade(ator, pedido.unidade_id)
            elif novo == StatusPedido.CANCELADO:
                if ator.perfil == PerfilUsuario.CLIENTE:
                    if pedido.cliente_id != ator.id:
                        raise AcessoNegadoError("Pedido de outro cliente")
                elif ator.perfil in (PerfilUsuario.ATENDENTE, PerfilUsuario.GERENTE_ADMIN):
                    exigir_mesma_unidade(ator, pedido.unidade_id)
                else:
                    raise AcessoNegadoError("Perfil sem permissão para cancelar")
                if not motivo:
                    raise ValidacaoError("Motivo é obrigatório no cancelamento",
                                         [{"field": "motivo", "issue": "obrigatório"}])
            else:
                raise ValidacaoError("Status não pode ser definido manualmente")

            validar_transicao(pedido.status, novo)
            self.pedidos.alterar_status(pedido, novo, ator.id, motivo)
            if novo == StatusPedido.CANCELADO:
                devolver_estoque(self.estoques, pedido, "Estorno - pedido cancelado")
            self.pedidos.commit()
        except Exception:
            self.pedidos.rollback()
            raise
        return pedido
