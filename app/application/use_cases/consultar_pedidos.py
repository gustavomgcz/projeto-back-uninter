from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.domain.exceptions import AcessoNegadoError, NaoEncontradoError
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.domain.value_objects.status_pedido import StatusPedido
from app.infrastructure.repositories.pedido_repository import PedidoRepository


class ConsultarPedidos:
    def __init__(self, pedidos: PedidoRepository):
        self.pedidos = pedidos

    def listar(self, ator, canal: CanalPedido | None, status: StatusPedido | None, page: int, limit: int):
        # cliente vê só os dele, o resto vê os da unidade
        cliente_id = ator.id if ator.perfil == PerfilUsuario.CLIENTE else None
        unidade_id = None if ator.perfil == PerfilUsuario.CLIENTE else ator.unidade_id
        return self.pedidos.listar(cliente_id=cliente_id, unidade_id=unidade_id, canal=canal,
                                   status=status, page=page, limit=limit)

    def obter(self, ator, pedido_id: int):
        pedido = self.pedidos.por_id(pedido_id)
        if pedido is None:
            raise NaoEncontradoError("Pedido não encontrado")
        if ator.perfil == PerfilUsuario.CLIENTE:
            if pedido.cliente_id != ator.id:
                raise AcessoNegadoError("Pedido de outro cliente")
        else:
            exigir_mesma_unidade(ator, pedido.unidade_id)
        return pedido
