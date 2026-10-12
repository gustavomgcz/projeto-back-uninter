from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_perfil
from app.api.schemas.common import Pagina, erros
from app.api.schemas.pedido import (
    PagamentoRequest, PagamentoResponse, PedidoCreate, PedidoResponse, StatusUpdate, pedido_response,
)
from app.application.use_cases.atualizar_status_pedido import AtualizarStatusPedido
from app.application.use_cases.consultar_pedidos import ConsultarPedidos
from app.application.use_cases.creditar_pontos_fidelidade import CreditarPontosFidelidade
from app.application.use_cases.criar_pedido import CriarPedido
from app.application.use_cases.solicitar_pagamento_mock import SolicitarPagamentoMock
from app.domain.entities.pedido import ItemSolicitado
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.perfil_usuario import PerfilUsuario as P
from app.domain.value_objects.status_pedido import StatusPedido
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.estoque_repository import EstoqueRepository
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository
from app.infrastructure.repositories.pedido_repository import PedidoRepository
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("", response_model=PedidoResponse, status_code=201, responses=erros(401, 403, 404, 409))
def criar_pedido(body: PedidoCreate, db: Session = Depends(get_db),
                 ator=Depends(require_perfil(P.CLIENTE, P.ATENDENTE))):
    pedido = CriarPedido(UnidadeRepository(db), ProdutoRepository(db), EstoqueRepository(db),
                         PedidoRepository(db), UsuarioRepository(db)).executar(
        ator, unidade_id=body.unidadeId, canal=body.canalPedido, cliente_id=body.clienteId,
        itens=[ItemSolicitado(i.produtoId, i.quantidade) for i in body.itens])
    return pedido_response(pedido)


@router.get("", response_model=Pagina[PedidoResponse], responses=erros(401))
def listar_pedidos(canalPedido: CanalPedido | None = None, status: StatusPedido | None = None,
                   page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
                   db: Session = Depends(get_db), ator=Depends(get_current_user)):
    itens, total = ConsultarPedidos(PedidoRepository(db)).listar(ator, canalPedido, status, page, limit)
    return Pagina(items=[pedido_response(p) for p in itens], page=page, limit=limit, total=total)


@router.get("/{pedido_id}", response_model=PedidoResponse, responses=erros(401, 403, 404))
def obter_pedido(pedido_id: int, db: Session = Depends(get_db), ator=Depends(get_current_user)):
    return pedido_response(ConsultarPedidos(PedidoRepository(db)).obter(ator, pedido_id))


@router.post("/{pedido_id}/pagamento", response_model=PagamentoResponse, responses=erros(401, 403, 404, 409))
def solicitar_pagamento(pedido_id: int, body: PagamentoRequest, db: Session = Depends(get_db),
                        ator=Depends(require_perfil(P.CLIENTE, P.ATENDENTE))):
    """Pagamento mockado: `forcarResultado` define aprovado/recusado; sem ele o resultado é determinístico."""
    pedidos = PedidoRepository(db)
    pedido = SolicitarPagamentoMock(
        pedidos, EstoqueRepository(db), CreditarPontosFidelidade(FidelidadeRepository(db)),
    ).executar(ator, pedido_id, body.formaPagamento, body.forcarResultado)
    return PagamentoResponse(pedidoId=pedido.id, resultado=pedido.pagamento.resultado, status=pedido.status,
                             respondidoEm=pedido.pagamento.respondido_em)


@router.patch("/{pedido_id}/status", response_model=PedidoResponse, responses=erros(401, 403, 404, 409))
def atualizar_status(pedido_id: int, body: StatusUpdate, db: Session = Depends(get_db),
                     ator=Depends(get_current_user)):
    pedido = AtualizarStatusPedido(PedidoRepository(db), EstoqueRepository(db)).executar(
        ator, pedido_id, body.novoStatus, body.motivo)
    return pedido_response(pedido)
