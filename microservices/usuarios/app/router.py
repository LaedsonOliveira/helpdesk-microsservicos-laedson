from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import limite, senhas, tokens
from app.auth.dependencias import exigir_perfil, usuario_atual
from app.database import get_db
from app.errors import NaoEncontrado, RegraDeNegocio
from app.model import Usuario
from app.schema import (
    Login,
    Perfil,
    TokenSaida,
    UsuarioCriar,
    UsuarioPublico,
    UsuarioSaida,
)
from app.service import buscar_por_email, criar, listar, obter

router = APIRouter()


@router.post("/auth/login", response_model=TokenSaida, tags=["Autenticação"])
def login(dados: Login, request: Request, db: Session = Depends(get_db)):
    email = str(dados.email).lower()
    chave = f"{email}|{request.client.host if request.client else '-'}"
    if limite.bloqueado(chave):
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Muitas tentativas. Tente de novo em alguns minutos.",
        )

    usuario = buscar_por_email(db, email)
    senha_ok = senhas.conferir(dados.senha, usuario.senha_hash if usuario else senhas.HASH_FALSO)
    if not usuario or not senha_ok or not usuario.ativo:
        limite.registrar_falha(chave)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos.")

    limite.limpar(chave)
    token, expira = tokens.criar(usuario.id, usuario.perfil)
    return TokenSaida(
        access_token=token,
        expira_em=expira,
        usuario=UsuarioSaida.model_validate(usuario),
    )


@router.get("/auth/eu", response_model=UsuarioSaida, tags=["Autenticação"])
def quem_sou_eu(usuario: Usuario = Depends(usuario_atual)):
    return usuario


@router.post(
    "/usuarios",
    response_model=UsuarioSaida,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuários"],
    dependencies=[Depends(exigir_perfil("admin"))],
)
def criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):
    try:
        return criar(db, dados)
    except RegraDeNegocio as erro:
        raise HTTPException(status.HTTP_409_CONFLICT, str(erro)) from erro


@router.get(
    "/usuarios",
    response_model=list[UsuarioPublico],
    tags=["Usuários"],
    dependencies=[Depends(usuario_atual)],
)
def listar_usuarios(perfil: Perfil | None = None, db: Session = Depends(get_db)):
    return listar(db, perfil)


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioPublico,
    tags=["Usuários"],
    responses={404: {"description": "Usuário não encontrado"}},
    dependencies=[Depends(usuario_atual)],
)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        return obter(db, usuario_id)
    except NaoEncontrado as erro:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(erro)) from erro
