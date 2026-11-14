from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import JWT_ALGORITMO, JWT_EMISSOR, JWT_SEGREDO

esquema = HTTPBearer(auto_error=False)
PERFIS = {"solicitante", "tecnico", "admin"}


@dataclass(frozen=True)
class UsuarioAutenticado:
    id: int
    perfil: str


def usuario_atual(
    credenciais: HTTPAuthorizationCredentials | None = Depends(esquema),
) -> UsuarioAutenticado:
    nao_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Faça login para continuar.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credenciais is None or credenciais.scheme.lower() != "bearer":
        raise nao_autenticado

    try:
        dados = jwt.decode(
            credenciais.credentials,
            JWT_SEGREDO,
            algorithms=[JWT_ALGORITMO],
            issuer=JWT_EMISSOR,
            options={"require": ["exp", "iat", "sub", "iss", "perfil"]},
        )
        usuario_id = int(dados["sub"])
        perfil = dados["perfil"]
        if usuario_id <= 0 or perfil not in PERFIS:
            raise ValueError("Claims inválidos.")
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as erro:
        raise nao_autenticado from erro

    return UsuarioAutenticado(id=usuario_id, perfil=perfil)


def exigir_perfil(*perfis: str):
    def verificar(usuario: UsuarioAutenticado = Depends(usuario_atual)) -> UsuarioAutenticado:
        if usuario.perfil not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para esta ação.",
            )
        return usuario

    return verificar
