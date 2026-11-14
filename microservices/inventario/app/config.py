"""Configurações do microserviço lidas do ambiente."""
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventario.db")

JWT_SEGREDO = os.getenv("JWT_SEGREDO", "")
if len(JWT_SEGREDO) < 32:
    raise RuntimeError("JWT_SEGREDO deve ser configurado com pelo menos 32 caracteres.")

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
TOKEN_MINUTOS = int(os.getenv("TOKEN_MINUTOS", "60"))
