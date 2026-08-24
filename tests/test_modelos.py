"""Testes da conversão da saída do modelo em flashcards validados."""

import pytest

from app.excecoes import ErroDoModelo
from app.modelos import Flashcard

JSON_LIMPO = '[{"pergunta": "O que e HTTP?", "resposta": "Um protocolo de aplicacao"}]'


def test_converte_json_limpo() -> None:
    cards = Flashcard.lista_de_resposta(JSON_LIMPO)
    assert cards == [Flashcard(pergunta="O que e HTTP?", resposta="Um protocolo de aplicacao")]


def test_aceita_json_dentro_de_cercas_markdown() -> None:
    cards = Flashcard.lista_de_resposta(f"```json\n{JSON_LIMPO}\n```")
    assert len(cards) == 1


def test_aceita_json_cercado_de_texto_explicativo() -> None:
    bruto = f"Claro! Aqui estao os flashcards:\n{JSON_LIMPO}\nEspero ter ajudado."
    assert len(Flashcard.lista_de_resposta(bruto)) == 1


def test_rejeita_resposta_sem_lista() -> None:
    with pytest.raises(ErroDoModelo):
        Flashcard.lista_de_resposta("Desculpe, nao consegui gerar flashcards.")


def test_rejeita_json_malformado() -> None:
    with pytest.raises(ErroDoModelo):
        Flashcard.lista_de_resposta('[{"pergunta": "sem fechar"')


def test_rejeita_itens_fora_do_formato_esperado() -> None:
    with pytest.raises(ErroDoModelo):
        Flashcard.lista_de_resposta('[{"pergunta": "faltou a resposta"}]')


def test_rejeita_lista_de_valores_que_nao_sao_objetos() -> None:
    with pytest.raises(ErroDoModelo):
        Flashcard.lista_de_resposta('["apenas", "strings"]')
