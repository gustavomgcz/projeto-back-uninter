def _pontos(client, s, email):
    return client.get("/fidelidade/saldo", headers=s.headers(email)).json()


def test_sem_consentimento_nao_credita(client, s):
    # cliente2 nunca consentiu
    antes = _pontos(client, s, "cliente2@raizes.com")["pontos"]
    pid = s.novo_produto("20.00")
    ped = s.pedido(pid, email="cliente2@raizes.com").json()["pedidoId"]
    assert s.pagar(ped, email="cliente2@raizes.com").status_code == 200
    depois = _pontos(client, s, "cliente2@raizes.com")
    assert depois["pontos"] == antes and depois["consentiu"] is False


def test_com_consentimento_credita_so_se_pago(client, s):
    h = s.headers("cliente@raizes.com")
    r = client.post("/fidelidade/consentimento", headers=h, json={"consentiu": True})
    assert r.status_code == 200 and r.json()["consentiu"] is True
    antes = _pontos(client, s, "cliente@raizes.com")["pontos"]

    pid = s.novo_produto("25.50", saldo=10)
    recusado = s.pedido(pid, qtd=2).json()["pedidoId"]
    s.pagar(recusado, "RECUSADO")
    assert _pontos(client, s, "cliente@raizes.com")["pontos"] == antes

    pago = s.pedido(pid, qtd=2).json()["pedidoId"]  # total 51.00 → 51 pontos
    s.pagar(pago, "APROVADO")
    saldo = _pontos(client, s, "cliente@raizes.com")
    assert saldo["pontos"] == antes + 51
    assert saldo["historico"][0]["pedidoId"] == pago


def test_saldo_so_do_proprio_cliente(client, s):
    assert client.get("/fidelidade/saldo").status_code == 401
    assert client.get("/fidelidade/saldo", headers=s.headers("gerente@raizes.com")).status_code == 403
    assert client.post("/fidelidade/consentimento", headers=s.headers("atendente@raizes.com"),
                       json={"consentiu": True}).status_code == 403
