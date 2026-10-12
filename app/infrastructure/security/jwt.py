from datetime import datetime, timedelta, timezone

import jwt

from app.domain.exceptions import NaoAutenticadoError
from app.settings import settings


def emitir_token(usuario_id: int, perfil: str) -> tuple[str, int]:
    expira_em = settings.jwt_expires_minutes * 60
    payload = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expira_em),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), expira_em


def validar_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise NaoAutenticadoError("Token inválido ou expirado")
