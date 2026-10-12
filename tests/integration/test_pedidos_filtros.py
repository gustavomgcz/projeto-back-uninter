def test_filtros_canal_e_status(client, s):
    pid = s.novo_produto(saldo=20)
    totem = s.pedido(pid, canal="TOTEM").json()["pedidoId"]
    s.pedido(pid, canal="WEB")
    s.pagar(totem)

    at = s.headers("atendente@raizes.com")
    r = client.get("/pedidos?canalPedido=TOTEM&limit=100", headers=at)
    assert r.status_code == 200
    assert r.json()["items"] and all(p["canalPedido"] == "TOTEM" for p in r.json()["items"])

    r = client.get("/pedidos?status=PAGO&limit=100", headers=s.headers("gerente@raizes.com"))
    assert totem in [p["pedidoId"] for p in r.json()["items"]]
    assert all(p["status"] == "PAGO" for p in r.json()["items"])

    r = client.get("/pedidos?status=AGUARDANDO_PAGAMENTO&canalPedido=WEB&limit=100", headers=at)
    assert all(p["status"] == "AGUARDANDO_PAGAMENTO" and p["canalPedido"] == "WEB" for p in r.json()["items"])
    assert client.get("/pedidos?canalPedido=FAX", headers=at).status_code == 422


def test_cliente_so_ve_os_proprios(client, s):
    pid = s.novo_produto(saldo=5)
    meu = s.pedido(pid, email="cliente2@raizes.com").json()["pedidoId"]
    s.pedido(pid, email="cliente@raizes.com")
    itens = client.get("/pedidos?limit=100", headers=s.headers("cliente2@raizes.com")).json()["items"]
    assert meu in [p["pedidoId"] for p in itens]
    assert len({p["clienteId"] for p in itens}) == 1


def test_paginacao(client, s):
    r = client.get("/pedidos?page=1&limit=1", headers=s.headers("atendente@raizes.com")).json()
    assert r["limit"] == 1 and len(r["items"]) <= 1 and r["total"] >= len(r["items"])
