# dados de exemplo: python -m app.infrastructure.db.seed
from decimal import Decimal

from sqlalchemy import select

from app.domain.value_objects.perfil_usuario import PerfilUsuario
from app.infrastructure.db.base import SessionLocal
from app.infrastructure.db.models import Estoque, Produto, Unidade, Usuario
from app.infrastructure.security.hashing import hash_senha

SENHA = "senha123"


def run() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Unidade.id).limit(1)):
            print("Seed já aplicado.")
            return
        u1 = Unidade(nome="Raízes Recife Centro", cidade="Recife", tipo_operacao="COZINHA_COMPLETA")
        u2 = Unidade(nome="Raízes Fortaleza Beira-Mar", cidade="Fortaleza", tipo_operacao="REDUZIDA")
        db.add_all([u1, u2])
        db.flush()
        for u in (u1, u2):
            for nome, preco in [("Baião de Dois", "29.90"), ("Carne de Sol com Macaxeira", "49.90"),
                                ("Tapioca de Queijo Coalho", "14.50"), ("Suco de Cajá", "9.00")]:
                p = Produto(nome=nome, preco=Decimal(preco), unidade_id=u.id)
                db.add(p)
                db.flush()
                db.add(Estoque(produto_id=p.id, unidade_id=u.id, saldo=50))
        usuarios = [
            ("Cliente Demo", "cliente@raizes.com", PerfilUsuario.CLIENTE, None),
            ("Cliente Dois", "cliente2@raizes.com", PerfilUsuario.CLIENTE, None),
            ("Atendente Demo", "atendente@raizes.com", PerfilUsuario.ATENDENTE, u1.id),
            ("Cozinha Demo", "cozinha@raizes.com", PerfilUsuario.COZINHA, u1.id),
            ("Gerente Demo", "gerente@raizes.com", PerfilUsuario.GERENTE_ADMIN, u1.id),
        ]
        for nome, email, perfil, unidade in usuarios:
            db.add(Usuario(nome=nome, email=email, senha_hash=hash_senha(SENHA), perfil=perfil, unidade_id=unidade))
        db.commit()
        print(f"Seed aplicado. Usuários demo (senha '{SENHA}'): " + ", ".join(e for _, e, _, _ in usuarios))


if __name__ == "__main__":
    run()
