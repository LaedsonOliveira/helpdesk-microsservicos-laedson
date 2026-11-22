"""Configurações do microserviço lidas do ambiente."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chamados.db")

JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("JWT_SEGREDO deve ser configurado com pelo menos 32 caracteres.")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
USUARIOS_URL = os.getenv("USUARIOS_URL", "http://usuarios:8000").rstrip("/")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://inventario:8000").rstrip("/")
TIMEOUT_SERVICOS_SEGUNDOS = float(os.getenv("TIMEOUT_SERVICOS_SEGUNDOS", "2"))
if TIMEOUT_SERVICOS_SEGUNDOS <= 0:
    raise RuntimeError("TIMEOUT_SERVICOS_SEGUNDOS deve ser maior que zero.")
