from app.domain.entities.usuario import validar_vinculo_unidade
from app.domain.exceptions import AcessoNegadoError, EmailJaCadastradoError, NaoEncontradoError
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.infrastructure.repositories.unidade_repository import UnidadeRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.hashing import hash_senha


class RegistrarUsuario:
    def __init__(self, usuarios: UsuarioRepository, unidades: UnidadeRepository):
        self.usuarios = usuarios
        self.unidades = unidades

    def executar(self, *, nome: str, email: str, senha: str, perfil: PerfilUsuario,
                 unidade_id: int | None, solicitante=None):
        # só gerente cria perfil operacional
        if perfil != PerfilUsuario.CLIENTE and (
            solicitante is None or solicitante.perfil != PerfilUsuario.GERENTE_ADMIN
        ):
            raise AcessoNegadoError("Apenas GERENTE_ADMIN pode criar perfis operacionais")
        validar_vinculo_unidade(perfil, unidade_id)
        if unidade_id is not None and self.unidades.por_id(unidade_id) is None:
            raise NaoEncontradoError("Unidade não encontrada")
        if self.usuarios.por_email(email):
            raise EmailJaCadastradoError("E-mail já cadastrado")
        usuario = self.usuarios.criar(nome=nome, email=email.lower(), senha_hash=hash_senha(senha),
                                      perfil=perfil, unidade_id=unidade_id)
        self.usuarios.commit()
        return usuario
