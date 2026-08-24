"""Construção dos prompts enviados ao modelo.

Isolados das rotas para que ajustes de prompt não impliquem mexer na camada HTTP.
"""


def prompt_resumo(texto: str) -> str:
    """Prompt que pede um resumo em tópicos do conteúdo extraído."""
    return (
        "Resuma o texto a seguir em tópicos objetivos, em português do Brasil, "
        "destacando os conceitos principais.\n\n"
        f"{texto}"
    )


def prompt_flashcards(texto: str) -> str:
    """Prompt que pede flashcards de estudo em JSON estrito."""
    return (
        "A partir do texto a seguir, gere de 5 a 10 flashcards de estudo em "
        "português do Brasil. Responda APENAS com uma lista JSON no formato "
        '[{"pergunta": "...", "resposta": "..."}], sem texto adicional e sem '
        "cercas de código.\n\n"
        f"{texto}"
    )
