from app.api.schemas.common import erros
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_optional
from app.api.schemas.auth import (
    LoginRequest, LoginResponse, RegistrarRequest, UsuarioResponse, UsuarioResumo,
)
from app.application.use_cases.autenticar_usuario import AutenticarUsuario
from app.application.use_cases.registrar_usuario import RegistrarUsuario
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.unidade_repository import UnidadeRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse, responses=erros(401))
def login(body: LoginRequest, db: Session = Depends(get_db)):
    usuario, token, expira = AutenticarUsuario(UsuarioRepository(db)).executar(body.email, body.senha)
    return LoginResponse(accessToken=token, expiresIn=expira,
                         user=UsuarioResumo(id=usuario.id, nome=usuario.nome, perfil=usuario.perfil))


@router.post("/registrar", response_model=UsuarioResponse, status_code=201, responses=erros(403, 404, 409))
def registrar(body: RegistrarRequest, db: Session = Depends(get_db),
              solicitante=Depends(get_current_user_optional)):
    """Público para CLIENTE; perfis operacionais exigem token de GERENTE_ADMIN."""
    u = RegistrarUsuario(UsuarioRepository(db), UnidadeRepository(db)).executar(
        nome=body.nome, email=body.email, senha=body.senha, perfil=body.perfil,
        unidade_id=body.unidadeId, solicitante=solicitante)
    return UsuarioResponse(id=u.id, nome=u.nome, email=u.email, perfil=u.perfil, unidadeId=u.unidade_id)
