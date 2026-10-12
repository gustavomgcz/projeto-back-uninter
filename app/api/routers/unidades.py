from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.schemas.common import Pagina, erros
from app.api.schemas.unidade import UnidadeResponse
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.unidade_repository import UnidadeRepository

router = APIRouter(prefix="/unidades", tags=["Unidades"])


@router.get("", response_model=Pagina[UnidadeResponse], responses=erros(401))
def listar_unidades(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100),
                    db: Session = Depends(get_db), _=Depends(get_current_user)):
    itens, total = UnidadeRepository(db).listar_ativas(page, limit)
    return Pagina(items=[UnidadeResponse(id=u.id, nome=u.nome, cidade=u.cidade, tipoOperacao=u.tipo_operacao)
                         for u in itens], page=page, limit=limit, total=total)
