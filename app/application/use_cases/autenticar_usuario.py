from app.domain.exceptions import CredenciaisInvalidasError
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.hashing import verificar_senha
from app.infrastructure.security.jwt import emitir_token


class AutenticarUsuario:
    def __init__(self, usuarios: UsuarioRepository):
        self.usuarios = usuarios

    def executar(self, email: str, senha: str):
        usuario = self.usuarios.por_email(email)
        # mesma resposta pra email inexistente e senha errada
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise CredenciaisInvalidasError("E-mail ou senha inválidos")
        token, expira_em = emitir_token(usuario.id, usuario.perfil.value)
        return usuario, token, expira_em
