class DomainError(Exception):
    # erro de regra de negócio, a API converte pra HTTP

    status_code = 409
    code = "ERRO_DE_DOMINIO"

    def __init__(self, message: str, details: list[dict] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class CredenciaisInvalidasError(DomainError):
    status_code = 401
    code = "CREDENCIAIS_INVALIDAS"


class NaoAutenticadoError(DomainError):
    status_code = 401
    code = "NAO_AUTENTICADO"


class AcessoNegadoError(DomainError):
    status_code = 403
    code = "ACESSO_NEGADO"


class NaoEncontradoError(DomainError):
    status_code = 404
    code = "NAO_ENCONTRADO"


class ValidacaoError(DomainError):
    status_code = 422
    code = "VALIDACAO"


class EmailJaCadastradoError(DomainError):
    code = "EMAIL_JA_CADASTRADO"


class EstoqueInsuficienteError(DomainError):
    code = "ESTOQUE_INSUFICIENTE"


class SaidaMaiorQueSaldoError(DomainError):
    code = "SAIDA_MAIOR_QUE_SALDO"


class ProdutoNaoPertenceAUnidadeError(DomainError):
    code = "PRODUTO_FORA_DA_UNIDADE"


class TransicaoStatusInvalidaError(DomainError):
    code = "TRANSICAO_INVALIDA"


class PagamentoJaProcessadoError(DomainError):
    code = "PAGAMENTO_JA_PROCESSADO"


class PedidoNaoAguardaPagamentoError(DomainError):
    code = "PEDIDO_NAO_AGUARDA_PAGAMENTO"


class FalhaPagamentoMockError(DomainError):
    status_code = 502
    code = "FALHA_PAGAMENTO_MOCK"
