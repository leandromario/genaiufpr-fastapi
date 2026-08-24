"""Testes de `ExtratorPDF` — camada de domínio, sem HTTP envolvido."""

import pytest

from app.excecoes import (
    ArquivoMuitoGrande,
    ErroDeExtracao,
    ExcessoDePaginas,
    LimiteExcedido,
    PdfInvalido,
    PdfSemTexto,
)
from app.extracao import ExtratorPDF
from tests.apoio import pdf_com_texto, pdf_em_branco


@pytest.fixture
def extrator() -> ExtratorPDF:
    return ExtratorPDF(max_paginas=30, max_mb=10)


def test_extrai_texto_de_pdf_valido(extrator: ExtratorPDF) -> None:
    texto = extrator.extrair(pdf_com_texto("Fotossintese converte luz em energia"))
    assert "Fotossintese converte luz em energia" in texto


def test_rejeita_arquivo_que_nao_e_pdf(extrator: ExtratorPDF) -> None:
    with pytest.raises(PdfInvalido):
        extrator.extrair(b"isto nao e um pdf")


def test_rejeita_pdf_sem_camada_de_texto(extrator: ExtratorPDF) -> None:
    with pytest.raises(PdfSemTexto):
        extrator.extrair(pdf_em_branco())


def test_rejeita_arquivo_acima_do_limite_de_tamanho() -> None:
    extrator = ExtratorPDF(max_paginas=30, max_mb=1)
    with pytest.raises(ArquivoMuitoGrande):
        extrator.extrair(b"\x00" * (2 * 1024 * 1024))


def test_rejeita_pdf_com_paginas_demais() -> None:
    extrator = ExtratorPDF(max_paginas=3, max_mb=10)
    with pytest.raises(ExcessoDePaginas):
        extrator.extrair(pdf_em_branco(paginas=4))


def test_limite_de_tamanho_e_verificado_antes_de_interpretar_o_pdf() -> None:
    """Bytes inválidos e grandes demais devem falhar por tamanho, não por parsing.

    A ordem importa: validar o tamanho primeiro evita gastar processamento (e,
    adiante no fluxo, créditos de API) com um arquivo que já seria recusado.
    """
    extrator = ExtratorPDF(max_paginas=30, max_mb=1)
    with pytest.raises(ArquivoMuitoGrande):
        extrator.extrair(b"nao e pdf" * 300_000)


def test_hierarquia_de_excecoes_define_os_status_http() -> None:
    assert issubclass(LimiteExcedido, ErroDeExtracao)
    assert ErroDeExtracao.status_code == 422
    assert PdfInvalido.status_code == 422
    assert PdfSemTexto.status_code == 422
    assert LimiteExcedido.status_code == 413
    assert ArquivoMuitoGrande.status_code == 413
    assert ExcessoDePaginas.status_code == 413
