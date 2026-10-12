from app.api.schemas.common import erros
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_perfil
from app.api.schemas.fidelidade import (
    ConsentimentoRequest, ConsentimentoResponse, MovimentoFidelidadeResponse, SaldoResponse,
)
from app.application.use_cases.consultar_saldo_fidelidade import ConsultarSaldoFidelidade
from app.application.use_cases.registrar_consentimento_fidelidade import RegistrarConsentimentoFidelidade
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.fidelidade_repository import FidelidadeRepository

router = APIRouter(prefix="/fidelidade", tags=["Fidelidade"])


@router.post("/consentimento", response_model=ConsentimentoResponse, responses=erros(401, 403))
def registrar_consentimento(body: ConsentimentoRequest, db: Session = Depends(get_db),
                            ator=Depends(require_perfil(PerfilUsuario.CLIENTE))):
    c = RegistrarConsentimentoFidelidade(FidelidadeRepository(db)).executar(ator.id, body.consentiu)
    return ConsentimentoResponse(consentiu=c.consentiu, registradoEm=c.registrado_em)


@router.get("/saldo", response_model=SaldoResponse, responses=erros(401, 403))
def consultar_saldo(db: Session = Depends(get_db), ator=Depends(require_perfil(PerfilUsuario.CLIENTE))):
    consentiu, pontos, hist = ConsultarSaldoFidelidade(FidelidadeRepository(db)).executar(ator.id)
    return SaldoResponse(consentiu=consentiu, pontos=pontos,
                         historico=[MovimentoFidelidadeResponse(pedidoId=m.pedido_id, pontos=m.pontos,
                                                                criadoEm=m.criado_em) for m in hist])
