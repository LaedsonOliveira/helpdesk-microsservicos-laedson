"""Regras do módulo de inventário. É a porta pública do módulo."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import NaoEncontrado, RegraDeNegocio
from app.model import Ativo
from app.repository import (
    buscar_por_id,
    buscar_por_patrimonio,
    listar as listar_repositorio,
    salvar,
)
from app.schema import AtivoCriar


def criar(db: Session, dados: AtivoCriar) -> Ativo:
    if buscar_por_patrimonio(db, dados.patrimonio):
        raise RegraDeNegocio("Já existe um ativo com este patrimônio.")
    try:
        return salvar(db, Ativo(**dados.model_dump()))
    except IntegrityError as erro:
        db.rollback()
        raise RegraDeNegocio("Já existe um ativo com este patrimônio.") from erro


def obter(db: Session, ativo_id: int) -> Ativo:
    ativo = buscar_por_id(db, ativo_id)
    if ativo is None:
        raise NaoEncontrado(f"Ativo {ativo_id} não encontrado.")
    return ativo


def listar(db: Session, setor: str | None = None) -> list[Ativo]:
    return listar_repositorio(db, setor)
