"""Ponto de entrada da aplicação: monta a app e traduz erros de domínio em HTTP."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import obter_configuracao
from app.excecoes import ErroDeExtracao, ErroDoModelo
from app.rotas import router, router_raiz


async def tratar_erro_de_dominio(request: Request, exc: Exception) -> JSONResponse:
    """Converte qualquer erro de domínio na resposta HTTP que ele declara.

    O status vem do atributo de classe da própria exceção, de modo que criar uma
    nova subclasse não exige tocar neste handler.
    """
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"detail": str(exc)},
    )


def criar_app() -> FastAPI:
    # Lê a configuração já na inicialização: sem NVIDIA_API_KEY o processo falha
    # aqui, em vez de só na primeira requisição.
    obter_configuracao()

    app = FastAPI(
        title="PDF Flashcards",
        description="Gera resumos e flashcards de estudo a partir de PDFs.",
    )
    app.include_router(router_raiz)
    app.include_router(router)
    app.add_exception_handler(ErroDeExtracao, tratar_erro_de_dominio)
    app.add_exception_handler(ErroDoModelo, tratar_erro_de_dominio)
    return app


app = criar_app()
