"""Utilitários de apoio aos testes: dublês e geração de PDFs sintéticos."""

import io

from pypdf import PdfWriter

from app.excecoes import ErroDoModelo
from app.gerador import GeradorDeTexto


class GeradorFake(GeradorDeTexto):
    """Dublê de `GeradorDeTexto` que não faz rede nem exige chave de API.

    Registra os prompts recebidos, para que os testes verifiquem o que teria
    sido enviado ao modelo, e permite simular falhas do provedor.
    """

    def __init__(self, resposta: str = "resposta de teste") -> None:
        self.resposta = resposta
        self.erro: ErroDoModelo | None = None
        self.prompts: list[str] = []

    def gerar(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.erro is not None:
            raise self.erro
        return self.resposta


def pdf_com_texto(texto: str) -> bytes:
    """Monta um PDF mínimo, porém válido, contendo `texto` em uma única página."""
    corpo = b"BT /F1 24 Tf 72 700 Td (" + texto.encode("latin-1") + b") Tj ET"
    objetos = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R"
        b"/Resources<</Font<</F1 5 0 R>>>>>>",
        b"<</Length %d>>stream\n%s\nendstream" % (len(corpo), corpo),
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]

    saida = bytearray(b"%PDF-1.4\n")
    deslocamentos = []
    for numero, objeto in enumerate(objetos, start=1):
        deslocamentos.append(len(saida))
        saida += b"%d 0 obj" % numero + objeto + b"endobj\n"

    inicio_xref = len(saida)
    saida += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for deslocamento in deslocamentos:
        saida += b"%010d 00000 n \n" % deslocamento
    saida += b"trailer<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objetos) + 1,
        inicio_xref,
    )
    return bytes(saida)


def pdf_em_branco(paginas: int = 1) -> bytes:
    """Monta um PDF válido sem camada de texto, com o número de páginas pedido."""
    escritor = PdfWriter()
    for _ in range(paginas):
        escritor.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    escritor.write(buffer)
    return buffer.getvalue()
