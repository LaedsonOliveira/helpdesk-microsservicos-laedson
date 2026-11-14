"""Limite em memória para tentativas repetidas de login."""
import time
from collections import defaultdict
from threading import Lock

from app.config import LOGIN_JANELA_SEGUNDOS, LOGIN_MAX_FALHAS

_falhas: dict[str, list[float]] = defaultdict(list)
_trava = Lock()


def _recentes(chave: str, agora: float) -> list[float]:
    _falhas[chave] = [instante for instante in _falhas[chave] if agora - instante < LOGIN_JANELA_SEGUNDOS]
    return _falhas[chave]


def bloqueado(chave: str) -> bool:
    with _trava:
        return len(_recentes(chave, time.monotonic())) >= LOGIN_MAX_FALHAS


def registrar_falha(chave: str) -> None:
    with _trava:
        _recentes(chave, time.monotonic()).append(time.monotonic())


def limpar(chave: str) -> None:
    with _trava:
        _falhas.pop(chave, None)
