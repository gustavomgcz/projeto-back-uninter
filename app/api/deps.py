from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.domain.exceptions import AcessoNegadoError, NaoAutenticadoError
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.infrastructure.db.base import get_db
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.jwt import validar_token

bearer = HTTPBearer(auto_error=False, description="Token JWT obtido em POST /auth/login")


def get_current_user_optional(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db),
):
    if cred is None:
        return None
    payload = validar_token(cred.credentials)
    usuario = UsuarioRepository(db).por_id(int(payload["sub"]))
    if usuario is None:
        raise NaoAutenticadoError("Usuário do token não existe mais")
    return usuario


def get_current_user(usuario=Depends(get_current_user_optional)):
    if usuario is None:
        raise NaoAutenticadoError("Autenticação necessária")
    return usuario


def require_perfil(*perfis: PerfilUsuario):
    def checker(usuario=Depends(get_current_user)):
        if usuario.perfil not in perfis:
            raise AcessoNegadoError("Perfil sem permissão para esta operação")
        return usuario
    return checker
