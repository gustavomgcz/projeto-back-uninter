from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.exceptions import DomainError

_HTTP_CODES = {400: "REQUISICAO_INVALIDA", 401: "NAO_AUTENTICADO", 403: "ACESSO_NEGADO",
               404: "NAO_ENCONTRADO", 405: "METODO_NAO_PERMITIDO", 409: "CONFLITO"}


def erro_json(request: Request, status: int, code: str, message: str, details: list | None = None):
    return JSONResponse(status_code=status, content={
        "error": code,
        "message": message,
        "details": details or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.url.path,
    })


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_handler(request: Request, exc: DomainError):
        return erro_json(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path")),
                    "issue": e["msg"]} for e in exc.errors()]
        return erro_json(request, 422, "VALIDACAO", "Dados da requisição inválidos", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        return erro_json(request, exc.status_code, _HTTP_CODES.get(exc.status_code, "ERRO_HTTP"),
                         str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected_handler(request: Request, exc: Exception):
        return erro_json(request, 500, "ERRO_INTERNO", "Erro interno do servidor")
