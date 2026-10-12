import os

import psycopg2
import pytest
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

TEST_DB = "raizes_test"
ADMIN_URL = os.getenv("TEST_ADMIN_DSN", "host=localhost port=5433 user=raizes password=raizes dbname=postgres")
os.environ["DATABASE_URL"] = f"postgresql+psycopg2://raizes:raizes@localhost:5433/{TEST_DB}"


def _recriar_banco() -> None:
    conn = psycopg2.connect(ADMIN_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB} WITH (FORCE)")
    cur.execute(f"CREATE DATABASE {TEST_DB}")
    conn.close()


@pytest.fixture(scope="session")
def client():
    _recriar_banco()
    from alembic import command
    from alembic.config import Config
    from fastapi.testclient import TestClient

    from app.api.main import app
    from app.infrastructure.db import seed

    command.upgrade(Config("alembic.ini"), "head")
    seed.run()
    with TestClient(app) as c:
        yield c


class Sessao:

    def __init__(self, client):
        self.client = client
        self._h: dict[str, dict] = {}

    def headers(self, email: str) -> dict:
        if email not in self._h:
            r = self.client.post("/auth/login", json={"email": email, "senha": "senha123"})
            assert r.status_code == 200, r.text
            self._h[email] = {"Authorization": f"Bearer {r.json()['accessToken']}"}
        return self._h[email]

    def novo_produto(self, preco="10.00", saldo=10, unidade_id=1) -> int:
        h = self.headers("gerente@raizes.com")
        r = self.client.post("/produtos", headers=h,
                             json={"nome": "Produto Teste", "preco": preco, "unidadeId": unidade_id})
        assert r.status_code == 201, r.text
        pid = r.json()["id"]
        if saldo:
            r = self.client.post("/estoque/movimentos", headers=h, json={
                "produtoId": pid, "unidadeId": unidade_id, "tipo": "ENTRADA", "quantidade": saldo})
            assert r.status_code == 201, r.text
        return pid

    def saldo(self, produto_id: int, unidade_id=1) -> int:
        r = self.client.get(f"/estoque?unidadeId={unidade_id}&produtoId={produto_id}",
                            headers=self.headers("gerente@raizes.com"))
        return r.json()["items"][0]["saldo"]

    def pedido(self, produto_id: int, qtd=1, canal="APP", email="cliente@raizes.com", unidade_id=1):
        return self.client.post("/pedidos", headers=self.headers(email), json={
            "unidadeId": unidade_id, "canalPedido": canal,
            "itens": [{"produtoId": produto_id, "quantidade": qtd}]})

    def pagar(self, pedido_id: int, resultado="APROVADO", email="cliente@raizes.com"):
        return self.client.post(f"/pedidos/{pedido_id}/pagamento", headers=self.headers(email),
                                json={"formaPagamento": "MOCK", "forcarResultado": resultado})


@pytest.fixture(scope="session")
def s(client):
    return Sessao(client)
