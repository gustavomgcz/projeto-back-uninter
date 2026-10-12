from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_perfil
from app.api.schemas.common import Pagina, erros
from app.api.schemas.estoque import EstoqueResponse, MovimentoEstoqueRequest, MovimentoEstoqueResponse
from app.application.use_cases.movimentar_estoque import ConsultarEstoque, MovimentarEstoque
from app.domain.value_objects.perfil_usuario import PerfilUsuario as P
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/estoque", tags=["Estoque"])


@router.post("/movimentos", response_model=MovimentoEstoqueResponse, status_code=201, responses=erros(401, 403, 404, 409))
def movimentar(body: MovimentoEstoqueRequest, db: Session = Depends(get_db),
               ator=Depends(require_perfil(P.ATENDENTE, P.GERENTE_ADMIN))):
    mov, est = MovimentarEstoque(EstoqueRepository(db)).executar(
        ator, produto_id=body.produtoId, unidade_id=body.unidadeId, tipo=body.tipo,
        quantidade=body.quantidade, motivo=body.motivo)
    return MovimentoEstoqueResponse(movimentoId=mov.id, tipo=mov.tipo, quantidade=mov.quantidade,
                                    saldoAtual=est.saldo)


@router.get("", response_model=Pagina[EstoqueResponse], responses=erros(401, 403))
def consultar(unidadeId: int = Query(...), produtoId: int | None = None,
              page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
              db: Session = Depends(get_db),
              ator=Depends(require_perfil(P.ATENDENTE, P.COZINHA, P.GERENTE_ADMIN))):
    itens, total = ConsultarEstoque(EstoqueRepository(db)).executar(ator, unidadeId, produtoId, page, limit)
    return Pagina(items=[EstoqueResponse(produtoId=e.produto_id, unidadeId=e.unidade_id, saldo=e.saldo,
                                         atualizadoEm=e.atualizado_em) for e in itens],
                  page=page, limit=limit, total=total)
