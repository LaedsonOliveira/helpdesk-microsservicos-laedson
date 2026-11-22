"""Regras de negócio do microserviço de Chamados."""
from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import repository
from app.auth.dependencias import UsuarioAutenticado
from app.config import INVENTARIO_URL, USUARIOS_URL
from app.errors import (
    ErroServicoDependente,
    NaoEncontrado,
    RegraDeNegocio,
    SemPermissao,
)
from app.integrations import obter_json
from app.model import Chamado, Comentario
from app.schema import ChamadoCriar, ComentarioCriar

HORAS_SLA = {"critica": 4, "alta": 8, "media": 24, "baixa": 72}
TRANSICOES = {
    "aberto": {"em_atendimento"},
    "em_atendimento": {"resolvido"},
    "resolvido": {"fechado", "em_atendimento"},
    "fechado": set(),
}
EQUIPE = ("tecnico", "admin")


def eh_equipe(usuario: UsuarioAutenticado) -> bool:
    return usuario.perfil in EQUIPE


def calcular_prazo(prioridade: str, inicio: datetime) -> datetime:
    return inicio + timedelta(hours=HORAS_SLA[prioridade])


def validar_ativo(ativo_id: int, usuario: UsuarioAutenticado) -> None:
    ativo = obter_json(
        f"{INVENTARIO_URL}/ativos/{ativo_id}",
        usuario.token,
        "Inventário",
        f"Ativo {ativo_id} não encontrado.",
    )
    if ativo.get("id") != ativo_id:
        raise ErroServicoDependente("O serviço de Inventário retornou um ativo inválido.")


def obter_tecnico(tecnico_id: int, usuario: UsuarioAutenticado) -> None:
    tecnico = obter_json(
        f"{USUARIOS_URL}/usuarios/{tecnico_id}",
        usuario.token,
        "Usuários",
        f"Usuário {tecnico_id} não encontrado.",
    )
    if tecnico.get("id") != tecnico_id or not isinstance(tecnico.get("perfil"), str):
        raise ErroServicoDependente("O serviço de Usuários retornou um usuário inválido.")
    if tecnico["perfil"] != "tecnico":
        raise RegraDeNegocio(f"Usuário {tecnico_id} não é técnico.")


def abrir(db: Session, dados: ChamadoCriar, usuario: UsuarioAutenticado) -> Chamado:
    if dados.ativo_id is not None:
        validar_ativo(dados.ativo_id, usuario)

    agora = datetime.now()
    chamado = repository.salvar(
        db,
        Chamado(
            **dados.model_dump(),
            solicitante_id=usuario.id,
            status="aberto",
            criado_em=agora,
            prazo_sla=calcular_prazo(dados.prioridade, agora),
        ),
    )
    return chamado


def obter(db: Session, chamado_id: int, usuario: UsuarioAutenticado) -> Chamado:
    chamado = repository.buscar_por_id(db, chamado_id)
    if chamado is None or not (
        eh_equipe(usuario) or chamado.solicitante_id == usuario.id
    ):
        raise NaoEncontrado(f"Chamado {chamado_id} não encontrado.")
    return chamado


def listar(
    db: Session,
    usuario: UsuarioAutenticado,
    status: str | None = None,
    tecnico_id: int | None = None,
) -> list[Chamado]:
    solicitante_id = None if eh_equipe(usuario) else usuario.id
    return repository.listar(db, status, tecnico_id, solicitante_id)


def atribuir(
    db: Session,
    chamado_id: int,
    tecnico_id: int,
    usuario: UsuarioAutenticado,
) -> Chamado:
    if not eh_equipe(usuario):
        raise SemPermissao("Só técnicos e administradores atribuem chamados.")
    chamado = obter(db, chamado_id, usuario)
    if chamado.status in ("resolvido", "fechado"):
        raise RegraDeNegocio("Não é possível atribuir um chamado resolvido ou fechado.")

    obter_tecnico(tecnico_id, usuario)
    chamado.tecnico_id = tecnico_id
    if chamado.status == "aberto":
        chamado.status = "em_atendimento"
    return repository.salvar(db, chamado)


def mudar_status(
    db: Session,
    chamado_id: int,
    novo_status: str,
    usuario: UsuarioAutenticado,
) -> Chamado:
    chamado = obter(db, chamado_id, usuario)
    pode_solicitante = chamado.status == "resolvido" and novo_status in (
        "fechado",
        "em_atendimento",
    )
    if not (eh_equipe(usuario) or pode_solicitante):
        raise SemPermissao("Você não pode mudar o status deste chamado.")
    if novo_status not in TRANSICOES[chamado.status]:
        raise RegraDeNegocio(
            f"Não é possível ir de '{chamado.status}' para '{novo_status}'."
        )
    if novo_status == "em_atendimento" and chamado.tecnico_id is None:
        raise RegraDeNegocio("Atribua um técnico antes de iniciar o atendimento.")

    chamado.status = novo_status
    return repository.salvar(db, chamado)


def comentar(
    db: Session,
    chamado_id: int,
    dados: ComentarioCriar,
    usuario: UsuarioAutenticado,
) -> Comentario:
    chamado = obter(db, chamado_id, usuario)
    if chamado.status == "fechado":
        raise RegraDeNegocio("Chamados fechados não recebem comentários.")
    return repository.salvar_comentario(
        db,
        Comentario(
            chamado_id=chamado.id,
            autor_id=usuario.id,
            texto=dados.texto,
            criado_em=datetime.now(),
        ),
    )


def painel(db: Session, usuario: UsuarioAutenticado) -> dict[str, int | dict[str, int]]:
    chamados = listar(db, usuario)
    agora = datetime.now()
    atrasados = sum(
        1
        for chamado in chamados
        if chamado.status in ("aberto", "em_atendimento")
        and chamado.prazo_sla < agora
    )
    return {
        "total": len(chamados),
        "por_status": dict(Counter(chamado.status for chamado in chamados)),
        "atrasados": atrasados,
    }
