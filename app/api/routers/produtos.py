from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_perfil
from app.api.schemas.common import Pagina, erros
from app.api.schemas.produto import ProdutoCreate, ProdutoResponse
from app.application.use_cases.cadastrar_produto import CadastrarProduto
from app.application.use_cases.consultar_cardapio import ConsultarCardapio
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.produto_repository import ProdutoRepository
from app.infrastructure.repositories.unidade_repository import UnidadeRepository

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _resp(p, saldo=None):
    return ProdutoResponse(id=p.id, nome=p.nome, descricao=p.descricao, preco=p.preco,
                           unidadeId=p.unidade_id, ativo=p.ativo, saldo=saldo)


@router.get("", response_model=Pagina[ProdutoResponse], responses=erros(401, 404))
def consultar_cardapio(unidadeId: int = Query(..., description="Unidade do cardápio"),
                       page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    itens, total = ConsultarCardapio(UnidadeRepository(db), ProdutoRepository(db)).executar(unidadeId, page, limit)
    return Pagina(items=[_resp(p, s) for p, s in itens], page=page, limit=limit, total=total)


@router.post("", response_model=ProdutoResponse, status_code=201, responses=erros(401, 403, 404))
def cadastrar_produto(body: ProdutoCreate, db: Session = Depends(get_db),
                      ator=Depends(require_perfil(PerfilUsuario.GERENTE_ADMIN))):
    p = CadastrarProduto(UnidadeRepository(db), ProdutoRepository(db)).executar(
        ator, nome=body.nome, descricao=body.descricao, preco=body.preco, unidade_id=body.unidadeId)
    return _resp(p, 0)
