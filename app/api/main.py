from fastapi import FastAPI

from app.api.error_handlers import registrar_handlers
from app.api.routers import auth, estoque, fidelidade, pedidos, produtos, unidades


def create_app() -> FastAPI:
    app = FastAPI(
        title="Raízes do Nordeste — API",
        version="0.1.0",
        description="Pedidos multicanal com pagamento **mock** e fidelização (LGPD).",
    )
    registrar_handlers(app)
    for r in (auth, unidades, produtos, estoque, pedidos, fidelidade):
        app.include_router(r.router)
    return app


app = create_app()
