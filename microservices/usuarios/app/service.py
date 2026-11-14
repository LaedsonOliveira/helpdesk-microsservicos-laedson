"""Regras do módulo de usuários. É a porta pública do módulo."""
from sqlalchemy.orm import Session

from app.auth import senhas
from app.errors import NaoEncontrado, RegraDeNegocio
from app.model import Usuario
from app.repository import buscar_por_email as repositorio_por_email
from app.repository import buscar_por_id as repositorio_por_id
from app.repository import listar as repositorio_listar
from app.repository import salvar as repositorio_salvar
from app.schema import UsuarioCriar


def criar(db: Session, dados: UsuarioCriar) -> Usuario:
    email = dados.email.lower()
    if repositorio_por_email(db, email):
        raise RegraDeNegocio("Já existe um usuário com este e-mail.")
    usuario = Usuario(nome=dados.nome, email=email, perfil=dados.perfil, senha_hash=senhas.gerar_hash(dados.senha))
    return repositorio_salvar(db, usuario)


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return repositorio_por_email(db, email.lower())


def obter(db: Session, usuario_id: int) -> Usuario:
    usuario = repositorio_por_id(db, usuario_id)
    if usuario is None:
        raise NaoEncontrado(f"Usuário {usuario_id} não encontrado.")
    return usuario


def obter_tecnico(db: Session, usuario_id: int) -> Usuario:
    usuario = obter(db, usuario_id)
    if usuario.perfil != "tecnico":
        raise RegraDeNegocio(f"Usuário {usuario_id} não é técnico.")
    return usuario


def listar(db: Session, perfil: str | None = None) -> list[Usuario]:
    return repositorio_listar(db, perfil)
