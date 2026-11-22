"""Clientes HTTP para os serviços dos quais Chamados depende."""
import httpx
from fastapi import HTTPException, status

from app.config import TIMEOUT_SERVICOS_SEGUNDOS
from app.errors import ErroServicoDependente, NaoEncontrado, ServicoIndisponivel


def obter_json(
    url: str,
    token: str,
    nome_servico: str,
    recurso_nao_encontrado: str,
) -> dict:
    try:
        resposta = httpx.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT_SERVICOS_SEGUNDOS,
        )
    except httpx.TimeoutException as erro:
        raise ServicoIndisponivel(
            f"O serviço de {nome_servico} não respondeu dentro do prazo."
        ) from erro
    except httpx.RequestError as erro:
        raise ServicoIndisponivel(
            f"Não foi possível conectar ao serviço de {nome_servico}."
        ) from erro

    if resposta.status_code == status.HTTP_404_NOT_FOUND:
        raise NaoEncontrado(recurso_nao_encontrado)
    if resposta.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        raise HTTPException(
            status_code=resposta.status_code,
            detail=f"O serviço de {nome_servico} recusou a autenticação.",
        )
    if resposta.is_error:
        if resposta.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise ServicoIndisponivel(
                f"O serviço de {nome_servico} está indisponível."
            )
        raise ErroServicoDependente(
            f"O serviço de {nome_servico} respondeu com HTTP {resposta.status_code}."
        )

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise ErroServicoDependente(
            f"O serviço de {nome_servico} retornou uma resposta inválida."
        ) from erro
    if not isinstance(dados, dict):
        raise ErroServicoDependente(
            f"O serviço de {nome_servico} retornou uma resposta inválida."
        )
    return dados
