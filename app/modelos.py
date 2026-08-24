"""Modelos de dados e schemas de resposta da API."""

import json

from pydantic import BaseModel, ValidationError

from app.excecoes import ErroDoModelo


class Flashcard(BaseModel):
    """Um cartão de estudo: uma pergunta e sua resposta."""

    pergunta: str
    resposta: str

    @classmethod
    def lista_de_resposta(cls, bruto: str) -> list["Flashcard"]:
        """Converte a saída textual do modelo em flashcards validados.

        Recorta do primeiro '[' ao último ']' porque alguns modelos envolvem o
        JSON em cercas markdown ou em texto explicativo, mesmo instruídos a não
        fazê-lo. A validação do formato fica por conta do próprio Pydantic.
        """
        inicio, fim = bruto.find("["), bruto.rfind("]")
        if inicio == -1 or fim < inicio:
            raise ErroDoModelo("O modelo não retornou uma lista JSON de flashcards")

        try:
            dados = json.loads(bruto[inicio : fim + 1])
        except json.JSONDecodeError as erro:
            raise ErroDoModelo(f"O modelo não retornou um JSON válido: {erro}") from erro

        try:
            return [cls.model_validate(item) for item in dados]
        except (ValidationError, TypeError) as erro:
            raise ErroDoModelo("O modelo retornou flashcards fora do formato esperado") from erro


class RespostaStatus(BaseModel):
    """Corpo devolvido por `GET /`.

    Informa o modelo em uso para que a verificação de um deploy não dependa de
    enviar um arquivo: basta abrir o endereço do servidor no navegador.
    """

    servico: str
    status: str
    modelo: str
    documentacao: str


class RespostaResumo(BaseModel):
    """Corpo devolvido por `POST /pdf/resumo`."""

    resumo: str


class RespostaFlashcards(BaseModel):
    """Corpo devolvido por `POST /pdf/flashcards`."""

    flashcards: list[Flashcard]
