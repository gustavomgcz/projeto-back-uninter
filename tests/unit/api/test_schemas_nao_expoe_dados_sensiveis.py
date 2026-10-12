import inspect

from app.api.schemas import auth, estoque, fidelidade, pedido, produto, unidade

PROIBIDOS = {"senha", "senha_hash", "senhaHash", "password", "hash", "payload_mock", "payloadMock"}


def _respostas():
    for mod in (auth, estoque, fidelidade, pedido, produto, unidade):
        for nome, cls in inspect.getmembers(mod, inspect.isclass):
            if nome.endswith("Response") or nome == "UsuarioResumo":
                yield nome, cls


def test_schemas_de_resposta_sem_campos_sensiveis():
    for nome, cls in _respostas():
        assert not (PROIBIDOS & set(cls.model_fields)), nome


def test_login_e_registro_nao_vazam_senha(client, s):
    r = client.post("/auth/registrar", json={"nome": "Novo", "email": "novo.sc4@raizes.com", "senha": "abc123"})
    assert r.status_code == 201
    assert "senha" not in r.text and "hash" not in r.text.lower()
    r = client.post("/auth/login", json={"email": "novo.sc4@raizes.com", "senha": "abc123"})
    assert "senha" not in r.text
    dup = client.post("/auth/registrar", json={"nome": "Novo", "email": "novo.sc4@raizes.com", "senha": "abc123"})
    assert dup.status_code == 409
    # perfil operacional exige GERENTE_ADMIN
    r = client.post("/auth/registrar", json={"nome": "X", "email": "x.sc4@raizes.com", "senha": "abc123",
                                             "perfil": "ATENDENTE", "unidadeId": 1})
    assert r.status_code == 403
