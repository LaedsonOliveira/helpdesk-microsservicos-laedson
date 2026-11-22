"""Erros de domínio do microserviço."""


class NaoEncontrado(Exception):
    """O recurso pedido não existe ou não está visível."""


class RegraDeNegocio(Exception):
    """A operação viola uma regra do sistema."""


class SemPermissao(Exception):
    """O usuário não tem permissão para a operação."""


class ServicoIndisponivel(Exception):
    """Um serviço dependente não respondeu dentro do prazo."""


class ErroServicoDependente(Exception):
    """Um serviço dependente respondeu com uma falha inesperada."""
