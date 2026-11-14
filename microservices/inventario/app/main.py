from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import inicializar_banco
from app.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    inicializar_banco()
    yield


app = FastAPI(title="Microserviço de Inventário", lifespan=lifespan)
app.include_router(router)


@app.get("/health", tags=["Saúde"])
@app.get("/saude", tags=["Saúde"])
def health():
    return {"status": "ok"}
