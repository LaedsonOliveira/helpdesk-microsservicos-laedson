from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.database import SessionLocal, inicializar_banco
from app.router import router
from app.schema import UsuarioCriar
from app.service import criar, listar


def preparar_banco() -> None:
    if bool(ADMIN_EMAIL) != bool(ADMIN_PASSWORD):
        raise RuntimeError("Configure ADMIN_EMAIL e ADMIN_PASSWORD juntos para criar o administrador inicial.")

    inicializar_banco()
    if not ADMIN_EMAIL:
        return

    with SessionLocal() as db:
        if listar(db):
            return
        criar(
            db,
            UsuarioCriar(
                nome="Admin TI",
                email=ADMIN_EMAIL,
                perfil="admin",
                senha=ADMIN_PASSWORD,
            ),
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    preparar_banco()
    yield


app = FastAPI(title="Microserviço de Usuários", lifespan=lifespan)
app.include_router(router)


@app.get("/health", tags=["Saúde"])
def health():
    return {"status": "ok"}