from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import inicializar_banco
from app.errors import (
    ErroServicoDependente,
    NaoEncontrado,
    RegraDeNegocio,
    SemPermissao,
    ServicoIndisponivel,
)
from app.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    inicializar_banco()
    yield


app = FastAPI(title="Microserviço de Chamados", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(NaoEncontrado)
def nao_encontrado(_: Request, erro: NaoEncontrado):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(erro)})


@app.exception_handler(RegraDeNegocio)
def regra_de_negocio(_: Request, erro: RegraDeNegocio):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(erro)})


@app.exception_handler(SemPermissao)
def sem_permissao(_: Request, erro: SemPermissao):
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(erro)})


@app.exception_handler(ServicoIndisponivel)
def servico_indisponivel(_: Request, erro: ServicoIndisponivel):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(erro)},
    )


@app.exception_handler(ErroServicoDependente)
def erro_servico_dependente(_: Request, erro: ErroServicoDependente):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(erro)},
    )


@app.get("/health", tags=["Saúde"])
@app.get("/saude", tags=["Saúde"])
def health():
    return {"status": "ok"}
