def test_fluxo_completo_aprovado(client, s):
    pid = s.novo_produto("39.90", saldo=10)
    h = s.headers("cliente@raizes.com")

    cardapio = client.get("/produtos?unidadeId=1", headers=h)
    assert cardapio.status_code == 200
    assert any(p["id"] == pid for p in cardapio.json()["items"]) or cardapio.json()["total"] > 0

    r = s.pedido(pid, qtd=2, canal="TOTEM")
    assert r.status_code == 201, r.text
    ped = r.json()
    assert ped["status"] == "AGUARDANDO_PAGAMENTO" and ped["canalPedido"] == "TOTEM"
    assert float(ped["total"]) == 79.80
    assert s.saldo(pid) == 8

    r = s.pagar(ped["pedidoId"], "APROVADO")
    assert r.status_code == 200 and r.json()["status"] == "PAGO"

    cozinha = s.headers("cozinha@raizes.com")
    for novo in ("EM_PREPARO", "PRONTO", "ENTREGUE"):
        r = client.patch(f"/pedidos/{ped['pedidoId']}/status", headers=cozinha, json={"novoStatus": novo})
        assert r.status_code == 200, r.text
        assert r.json()["status"] == novo

    final = client.get(f"/pedidos/{ped['pedidoId']}", headers=h).json()
    assert [x["statusNovo"] for x in final["historico"]] == [
        "AGUARDANDO_PAGAMENTO", "PAGO", "EM_PREPARO", "PRONTO", "ENTREGUE"]


def test_pagamento_recusado_estorna_estoque(client, s):
    pid = s.novo_produto(saldo=5)
    ped = s.pedido(pid, qtd=3).json()
    assert s.saldo(pid) == 2
    r = s.pagar(ped["pedidoId"], "RECUSADO")
    assert r.status_code == 200 and r.json()["status"] == "PAGAMENTO_RECUSADO"
    assert s.saldo(pid) == 5


def test_estoque_insuficiente_nao_debita_nem_cria_pedido(client, s):
    pid = s.novo_produto(saldo=2)
    r = s.pedido(pid, qtd=3)
    assert r.status_code == 409 and r.json()["error"] == "ESTOQUE_INSUFICIENTE"
    assert s.saldo(pid) == 2


def test_pedido_inteiro_rejeitado_se_um_item_invalido(client, s):
    ok, pouco = s.novo_produto(saldo=10), s.novo_produto(saldo=1)
    r = client.post("/pedidos", headers=s.headers("cliente@raizes.com"), json={
        "unidadeId": 1, "canalPedido": "APP",
        "itens": [{"produtoId": ok, "quantidade": 2}, {"produtoId": pouco, "quantidade": 5}]})
    assert r.status_code == 409
    assert s.saldo(ok) == 10  # nenhum débito parcial


def test_canal_obrigatorio_e_valido(client, s):
    pid = s.novo_produto()
    h = s.headers("cliente@raizes.com")
    r = client.post("/pedidos", headers=h, json={"unidadeId": 1, "itens": [{"produtoId": pid, "quantidade": 1}]})
    assert r.status_code == 422 and r.json()["error"] == "VALIDACAO"
    r = s.pedido(pid, canal="FAX")
    assert r.status_code == 422


def test_produto_de_outra_unidade(client, s):
    # produto da unidade 2: ids altos; busca pelo cardápio da unidade 2
    h = s.headers("cliente@raizes.com")
    prod = client.get("/produtos?unidadeId=2", headers=h).json()["items"][0]
    r = s.pedido(prod["id"], unidade_id=1)
    assert r.status_code == 409 and r.json()["error"] == "PRODUTO_FORA_DA_UNIDADE"


def test_pagamento_duplicado_e_transicao_invalida(client, s):
    pid = s.novo_produto()
    ped = s.pedido(pid).json()["pedidoId"]
    assert s.pagar(ped).status_code == 200
    r = s.pagar(ped)
    assert r.status_code == 409 and r.json()["error"] == "PAGAMENTO_JA_PROCESSADO"

    cozinha = s.headers("cozinha@raizes.com")
    r = client.patch(f"/pedidos/{ped}/status", headers=cozinha, json={"novoStatus": "PRONTO"})
    assert r.status_code == 409 and r.json()["error"] == "TRANSICAO_INVALIDA"
    client.patch(f"/pedidos/{ped}/status", headers=cozinha, json={"novoStatus": "EM_PREPARO"})
    client.patch(f"/pedidos/{ped}/status", headers=cozinha, json={"novoStatus": "PRONTO"})
    client.patch(f"/pedidos/{ped}/status", headers=cozinha, json={"novoStatus": "ENTREGUE"})
    r = client.patch(f"/pedidos/{ped}/status", headers=cozinha, json={"novoStatus": "EM_PREPARO"})
    assert r.status_code == 409
    r = client.patch(f"/pedidos/{ped}/status", headers=s.headers("cliente@raizes.com"),
                     json={"novoStatus": "CANCELADO", "motivo": "x"})
    assert r.status_code == 409  # já entregue


def test_cancelamento_devolve_estoque(client, s):
    pid = s.novo_produto(saldo=4)
    ped = s.pedido(pid, qtd=4).json()["pedidoId"]
    h = s.headers("cliente@raizes.com")
    r = client.patch(f"/pedidos/{ped}/status", headers=h, json={"novoStatus": "CANCELADO"})
    assert r.status_code == 422  # motivo obrigatório
    r = client.patch(f"/pedidos/{ped}/status", headers=h, json={"novoStatus": "CANCELADO", "motivo": "desisti"})
    assert r.status_code == 200 and r.json()["motivoCancelamento"] == "desisti"
    assert s.saldo(pid) == 4


def test_autenticacao_e_autorizacao(client, s):
    assert client.get("/pedidos").status_code == 401
    r = client.post("/auth/login", json={"email": "cliente@raizes.com", "senha": "errada"})
    r2 = client.post("/auth/login", json={"email": "naoexiste@raizes.com", "senha": "errada"})
    assert r.status_code == r2.status_code == 401 and r.json()["message"] == r2.json()["message"]
    pid = s.novo_produto()
    ped = s.pedido(pid).json()["pedidoId"]
    # cliente 2 não paga nem vê o pedido do cliente 1
    assert s.pagar(ped, email="cliente2@raizes.com").status_code == 403
    assert client.get(f"/pedidos/{ped}", headers=s.headers("cliente2@raizes.com")).status_code == 403
    # cozinha não cria pedido; cliente não cadastra produto
    assert s.pedido(pid, email="cozinha@raizes.com").status_code == 403
    r = client.post("/produtos", headers=s.headers("cliente@raizes.com"),
                    json={"nome": "x", "preco": "1.00", "unidadeId": 1})
    assert r.status_code == 403
    assert client.get("/pedidos/999999", headers=s.headers("cliente@raizes.com")).status_code == 404


def test_formato_de_erro_padrao(client, s):
    r = client.get("/pedidos/999999", headers=s.headers("cliente@raizes.com"))
    body = r.json()
    assert set(body) >= {"error", "message", "details", "timestamp", "path"}
    assert body["path"] == "/pedidos/999999"
