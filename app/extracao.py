"""Extração de texto de arquivos PDF."""

import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.excecoes import ArquivoMuitoGrande, ExcessoDePaginas, PdfInvalido, PdfSemTexto


class ExtratorPDF:
    """Lê PDFs respeitando limites de tamanho e de páginas.

    Recebe `bytes` em vez de um `UploadFile` para não depender do FastAPI: a
    mesma classe serve a um endpoint HTTP, a um script de linha de comando ou a
    um worker em segundo plano.
    """

    def __init__(self, max_paginas: int, max_mb: int) -> None:
        self._max_paginas = max_paginas
        self._max_mb = max_mb

    def extrair(self, conteudo: bytes) -> str:
        """Devolve o texto do PDF, validando-o antes de qualquer processamento caro."""
        if len(conteudo) > self._max_mb * 1024 * 1024:
            raise ArquivoMuitoGrande(f"PDF excede o limite de {self._max_mb} MB")

        try:
            paginas = PdfReader(io.BytesIO(conteudo)).pages
        except (PdfReadError, OSError, ValueError) as erro:
            raise PdfInvalido(f"Não foi possível ler o arquivo como PDF: {erro}") from erro

        if len(paginas) > self._max_paginas:
            raise ExcessoDePaginas(f"PDF excede o limite de {self._max_paginas} páginas")

        texto = "\n".join(pagina.extract_text() or "" for pagina in paginas)
        if not texto.strip():
            raise PdfSemTexto(
                "Nenhum texto extraível encontrado no PDF (o arquivo pode ser digitalizado)"
            )
        return texto
