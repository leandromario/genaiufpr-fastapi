"""Exceções de domínio da aplicação.

Nenhuma delas conhece HTTP: cada classe apenas declara o status que a representa,
e a tradução para uma resposta HTTP acontece nos handlers registrados em `main`.
Isso mantém as camadas de extração e geração reutilizáveis fora do FastAPI.
"""


class ErroDeExtracao(Exception):
    """Falha ao obter texto utilizável do PDF enviado."""

    status_code = 422


class PdfInvalido(ErroDeExtracao):
    """O arquivo enviado não pôde ser interpretado como PDF."""


class PdfSemTexto(ErroDeExtracao):
    """O PDF é legível, mas não possui camada de texto (provavelmente digitalizado)."""


class LimiteExcedido(ErroDeExtracao):
    """O PDF ultrapassa os limites aceitos pela API."""

    status_code = 413


class ArquivoMuitoGrande(LimiteExcedido):
    """O arquivo excede o tamanho máximo em bytes."""


class ExcessoDePaginas(LimiteExcedido):
    """O PDF excede o número máximo de páginas."""


class ErroDoModelo(Exception):
    """Falha ao obter uma resposta utilizável do modelo de linguagem."""

    status_code = 502
