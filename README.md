# Raízes do Nordeste — API Back-end

API (Python 3.11+ / FastAPI / PostgreSQL) de pedidos multicanal com pagamento mockado e fidelização com consentimento LGPD.

## Arquitetura (4 camadas)

`app/domain` → `app/application/use_cases` → `app/infrastructure` (SQLAlchemy, Alembic, JWT, mock de pagamento) e `app/api` (FastAPI, schemas, rotas).

## Como rodar

```bash
cp .env.example .env
docker compose up -d db                 # Postgres na porta 5433 (ou aponte DATABASE_URL para o seu)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.infrastructure.db.seed
uvicorn app.api.main:app --reload
```

- Swagger: http://localhost:8000/docs · OpenAPI: http://localhost:8000/openapi.json
- Usuários demo (senha `senha123`): `cliente@raizes.com`, `cliente2@raizes.com`, `atendente@raizes.com`, `cozinha@raizes.com`, `gerente@raizes.com`

## Fluxo

`POST /auth/login` → `GET /produtos?unidadeId=1` → `POST /pedidos` (com `canalPedido`) → `POST /pedidos/{id}/pagamento` (`forcarResultado`: `APROVADO`/`RECUSADO`) → `PATCH /pedidos/{id}/status` (`EM_PREPARO` → `PRONTO` → `ENTREGUE`).

## Decisões de regra de negócio

- O estoque é debitado na criação do pedido (com lock de linha) e devolvido se o pagamento for recusado ou o pedido cancelado.
- Pagamento é mock: sem `forcarResultado`, o resultado é determinístico pelo id do pedido. Nenhum pagamento real é processado.
- Pontos: 1 ponto por real inteiro pago, somente com consentimento registrado e pagamento aprovado.
- Perfis operacionais (ATENDENTE/COZINHA/GERENTE_ADMIN) atuam apenas na própria unidade.
- Auditoria: histórico de status do pedido (`historico`) e movimentos de estoque. Não há log de auditoria genérico.

## Testes

```bash
pytest                                   # usa o banco raizes_test (recriado a cada execução, Postgres da porta 5433)
npx newman run tests/contract/postman/raizes-do-nordeste.postman_collection.json   # API no ar + seed
```

A coleção Postman está em `tests/contract/postman/` (usa `{{baseUrl}}`; tokens são preenchidos pelos logins).
