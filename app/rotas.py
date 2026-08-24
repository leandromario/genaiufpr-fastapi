"""Endpoints HTTP da API.

As rotas são deliberadamente finas: validam a entrada, orquestram extrator e
gerador, e devolvem o modelo de resposta. Erros de domínio sobem para os
handlers registrados em `main`.
"""

from fastapi import APIRouter, Depends, UploadFile

from app.config import Configuracao, obter_configuracao
from app.dependencias import obter_extrator, obter_gerador
from app.extracao import ExtratorPDF
from app.gerador import GeradorDeTexto
from app.modelos import Flashcard, RespostaFlashcards, RespostaResumo, RespostaStatus
from app.prompts import prompt_flashcards, prompt_resumo

router_raiz = APIRouter(tags=["status"])
router = APIRouter(prefix="/pdf", tags=["pdf"])


@router_raiz.get("/", response_model=RespostaStatus)
async def status(config: Configuracao = Depends(obter_configuracao)) -> RespostaStatus:
    """Confirma que o serviço está no ar e informa qual modelo está configurado."""
    return RespostaStatus(
        servico="PDF Flashcards",
        status="ok",
        modelo=config.nim_model,
        documentacao="/docs",
    )


@router.post("/resumo", response_model=RespostaResumo)
async def gerar_resumo(
    arquivo: UploadFile,
    extrator: ExtratorPDF = Depends(obter_extrator),
    gerador: GeradorDeTexto = Depends(obter_gerador),
) -> RespostaResumo:
    """Resume o conteúdo do PDF enviado em tópicos."""
    texto = extrator.extrair(await arquivo.read())
    return RespostaResumo(resumo=gerador.gerar(prompt_resumo(texto)))


@router.post("/flashcards", response_model=RespostaFlashcards)
async def gerar_flashcards(
    arquivo: UploadFile,
    extrator: ExtratorPDF = Depends(obter_extrator),
    gerador: GeradorDeTexto = Depends(obter_gerador),
) -> RespostaFlashcards:
    """Gera flashcards de estudo (pergunta/resposta) a partir do PDF enviado."""
    texto = extrator.extrair(await arquivo.read())
    bruto = gerador.gerar(prompt_flashcards(texto))
    return RespostaFlashcards(flashcards=Flashcard.lista_de_resposta(bruto))
