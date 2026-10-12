from app.application.use_cases._autorizacao import exigir_mesma_unidade
from app.domain.entities.pedido import ItemSolicitado, ProdutoDisponivel, validar_e_totalizar
from app.domain.exceptions import AcessoNegadoError, NaoEncontradoError, ValidacaoError
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque
from app.infrastructure.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.repositories.pedido_repository import PedidoRepository
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository


class CriarPedido:
    def __init__(self, unidades: UnidadeRepository, produtos: ProdutoRepository,
                 estoques: EstoqueRepository, pedidos: PedidoRepository, usuarios: UsuarioRepository):
        self.unidades = unidades
        self.produtos = produtos
        self.estoques = estoques
        self.pedidos = pedidos
        self.usuarios = usuarios

    def executar(self, ator, *, unidade_id: int, canal: CanalPedido, itens: list[ItemSolicitado],
                 cliente_id: int | None = None):
        if ator.perfil == PerfilUsuario.CLIENTE:
            cliente_id = ator.id
        elif ator.perfil == PerfilUsuario.ATENDENTE:
            exigir_mesma_unidade(ator, unidade_id)
            if cliente_id is None:
                raise ValidacaoError("ATENDENTE deve informar clienteId",
                                     [{"field": "clienteId", "issue": "obrigatório para ATENDENTE"}])
            cliente = self.usuarios.por_id(cliente_id)
            if cliente is None or cliente.perfil != PerfilUsuario.CLIENTE:
                raise NaoEncontradoError("Cliente não encontrado")
        else:
            raise AcessoNegadoError("Perfil sem permissão para criar pedidos")

        if self.unidades.por_id(unidade_id) is None:
            raise NaoEncontradoError("Unidade não encontrada")

        ids = sorted({i.produto_id for i in itens})
        produtos = {}
        for pid in ids:
            produto = self.produtos.por_id(pid)
            if produto is None:
                raise NaoEncontradoError(f"Produto {pid} não encontrado")
            produtos[pid] = produto

        try:
            estoques = self.estoques.obter_varios_com_lock(ids, unidade_id)
            disponiveis = {
                pid: ProdutoDisponivel(
                    id=pid, nome=p.nome, preco=p.preco, unidade_id=p.unidade_id, ativo=p.ativo,
                    saldo=estoques[pid].saldo if pid in estoques else 0,
                )
                for pid, p in produtos.items()
            }
            total = validar_e_totalizar(unidade_id, itens, disponiveis)

            agregadas: dict[int, int] = {}
            for i in itens:
                agregadas[i.produto_id] = agregadas.get(i.produto_id, 0) + i.quantidade
            linhas = [(pid, q, produtos[pid].preco) for pid, q in agregadas.items()]

            pedido = self.pedidos.criar(cliente_id, unidade_id, canal, total, linhas, ator.id)
            for pid, q in agregadas.items():
                est = estoques[pid]
                self.estoques.registrar_movimento(est, TipoMovimentoEstoque.SAIDA, q, est.saldo - q,
                                                  motivo="Venda - pedido", pedido_id=pedido.id)
            self.pedidos.commit()
        except Exception:
            self.pedidos.rollback()
            raise
        return pedido
