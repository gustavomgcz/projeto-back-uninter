def test_entrada_saida_e_saldo(client, s):
    pid = s.novo_produto(saldo=0)
    h = s.headers("gerente@raizes.com")
    assert s.saldo(pid) == 0
    mov = {"produtoId": pid, "unidadeId": 1, "quantidade": 7}
    r = client.post("/estoque/movimentos", headers=h, json={**mov, "tipo": "ENTRADA"})
    assert r.status_code == 201 and r.json()["saldoAtual"] == 7
    r = client.post("/estoque/movimentos", headers=h, json={**mov, "tipo": "SAIDA", "quantidade": 3, "motivo": "perda"})
    assert r.status_code == 201 and r.json()["saldoAtual"] == 4
    r = client.post("/estoque/movimentos", headers=h, json={**mov, "tipo": "SAIDA", "quantidade": 5, "motivo": "perda"})
    assert r.status_code == 409 and r.json()["error"] == "SAIDA_MAIOR_QUE_SALDO"
    assert s.saldo(pid) == 4


def test_produto_sem_estoque_nao_vende(client, s):
    pid = s.novo_produto(saldo=0)
    r = s.pedido(pid)
    assert r.status_code == 409 and r.json()["error"] == "ESTOQUE_INSUFICIENTE"


def test_permissoes_de_estoque(client, s):
    pid = s.novo_produto()
    body = {"produtoId": pid, "unidadeId": 1, "tipo": "ENTRADA", "quantidade": 1}
    assert client.post("/estoque/movimentos", headers=s.headers("cliente@raizes.com"), json=body).status_code == 403
    assert client.post("/estoque/movimentos", headers=s.headers("cozinha@raizes.com"), json=body).status_code == 403
    assert client.post("/estoque/movimentos", json=body).status_code == 401
    # outra unidade
    r = client.get("/estoque?unidadeId=2", headers=s.headers("gerente@raizes.com"))
    assert r.status_code == 403
