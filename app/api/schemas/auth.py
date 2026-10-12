from pydantic import BaseModel, EmailStr, Field

from app.domain.value_objects.perfil_usuario import PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class UsuarioResumo(BaseModel):
    id: int
    nome: str
    perfil: PerfilUsuario


class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    user: UsuarioResumo


class RegistrarRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)
    perfil: PerfilUsuario = PerfilUsuario.CLIENTE
    unidadeId: int | None = None


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    unidadeId: int | None
