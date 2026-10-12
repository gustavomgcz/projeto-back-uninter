from sqlalchemy import select

from app.infrastructure.db.models import Usuario
from app.infrastructure.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository):
    def por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.email == email.lower()))

    def por_id(self, usuario_id: int) -> Usuario | None:
        return self.db.get(Usuario, usuario_id)

    def criar(self, **dados) -> Usuario:
        usuario = Usuario(**dados)
        self.db.add(usuario)
        self.db.flush()
        return usuario
