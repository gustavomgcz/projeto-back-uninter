from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    JSON, Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.pagamento import ResultadoPagamento
from app.domain.value_objects.canal_pedido import CanalPedido
from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.domain.value_objects.status_pedido import StatusPedido
from app.domain.value_objects.tipo_movimento_estoque import TipoMovimentoEstoque
from app.infrastructure.db.base import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _enum(cls, name: str):
    return SAEnum(cls, name=name, native_enum=False, length=32, validate_strings=True)


class Unidade(Base):
    __tablename__ = "unidades"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    cidade: Mapped[str | None] = mapped_column(String(80))
    tipo_operacao: Mapped[str] = mapped_column(String(32), default="COZINHA_COMPLETA")
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)


class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    perfil: Mapped[PerfilUsuario] = mapped_column(_enum(PerfilUsuario, "perfil_usuario"))
    unidade_id: Mapped[int | None] = mapped_column(ForeignKey("unidades.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Produto(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str | None] = mapped_column(String(500))
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), index=True)


class Estoque(Base):
    __tablename__ = "estoques"
    __table_args__ = (UniqueConstraint("produto_id", "unidade_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    saldo: Mapped[int] = mapped_column(Integer, default=0)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class MovimentoEstoque(Base):
    __tablename__ = "movimentos_estoque"
    id: Mapped[int] = mapped_column(primary_key=True)
    estoque_id: Mapped[int] = mapped_column(ForeignKey("estoques.id"), index=True)
    tipo: Mapped[TipoMovimentoEstoque] = mapped_column(_enum(TipoMovimentoEstoque, "tipo_movimento_estoque"))
    quantidade: Mapped[int] = mapped_column(Integer)
    motivo: Mapped[str | None] = mapped_column(String(255))
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Pedido(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), index=True)
    canal_pedido: Mapped[CanalPedido] = mapped_column(_enum(CanalPedido, "canal_pedido"), index=True)
    status: Mapped[StatusPedido] = mapped_column(_enum(StatusPedido, "status_pedido"), index=True)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    motivo_cancelamento: Mapped[str | None] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    itens: Mapped[list["ItemPedido"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    historico: Mapped[list["HistoricoStatusPedido"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin", order_by="HistoricoStatusPedido.id"
    )
    pagamento: Mapped["Pagamento | None"] = relationship(uselist=False, lazy="selectin")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    quantidade: Mapped[int] = mapped_column(Integer)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class HistoricoStatusPedido(Base):
    __tablename__ = "historico_status_pedido"
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), index=True)
    status_anterior: Mapped[StatusPedido | None] = mapped_column(_enum(StatusPedido, "status_pedido_ant"))
    status_novo: Mapped[StatusPedido] = mapped_column(_enum(StatusPedido, "status_pedido_novo"))
    alterado_por: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Pagamento(Base):
    __tablename__ = "pagamentos"
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True)
    resultado: Mapped[ResultadoPagamento] = mapped_column(_enum(ResultadoPagamento, "resultado_pagamento"))
    payload_mock: Mapped[dict] = mapped_column(JSON)
    solicitado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    respondido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ConsentimentoFidelidade(Base):
    __tablename__ = "consentimentos_fidelidade"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    consentiu: Mapped[bool] = mapped_column(Boolean)
    registrado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SaldoFidelidade(Base):
    __tablename__ = "saldos_fidelidade"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    pontos: Mapped[int] = mapped_column(Integer, default=0)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class MovimentoFidelidade(Base):
    __tablename__ = "movimentos_fidelidade"
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    pontos: Mapped[int] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
