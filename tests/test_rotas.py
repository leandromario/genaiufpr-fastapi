"""Testes dos endpoints HTTP, exercitados sem rede via `GeradorFake`."""

from fastapi.testclient import TestClient

from app.excecoes import ErroDoModelo
from tests.apoio import GeradorFake, pdf_com_texto, pdf_em_branco

PDF = pdf_com_texto("Redes de computadores transmitem pacotes")
FLASHCARDS_JSON = '[{"pergunta": "O que e um pacote?", "resposta": "Unidade de dados"}]'


def _enviar(cliente: TestClient, rota: str, conteudo: bytes, nome: str = "aula.pdf"):
    return cliente.post(rota, files={"arquivo": (nome, conteudo, "application/pdf")})


def test_resumo_devolve_o_texto_gerado(cliente: TestClient, gerador_fake: GeradorFake) -> None:
    gerador_fake.resposta = "- Pacotes trafegam pela rede"

    resposta = _enviar(cliente, "/pdf/resumo", PDF)

    assert resposta.status_code == 200
    assert resposta.json() == {"resumo": "- Pacotes trafegam pela rede"}


def test_resumo_envia_o_conteudo_extraido_ao_modelo(
    cliente: TestClient, gerador_fake: GeradorFake
) -> None:
    _enviar(cliente, "/pdf/resumo", PDF)

    assert len(gerador_fake.prompts) == 1
    assert "Redes de computadores transmitem pacotes" in gerador_fake.prompts[0]


def test_flashcards_devolve_cartoes_estruturados(
    cliente: TestClient, gerador_fake: GeradorFake
) -> None:
    gerador_fake.resposta = FLASHCARDS_JSON

    resposta = _enviar(cliente, "/pdf/flashcards", PDF)

    assert resposta.status_code == 200
    assert resposta.json() == {
        "flashcards": [{"pergunta": "O que e um pacote?", "resposta": "Unidade de dados"}]
    }


def test_arquivo_que_nao_e_pdf_resulta_em_422(cliente: TestClient) -> None:
    resposta = _enviar(cliente, "/pdf/resumo", b"isto nao e um pdf", nome="notas.txt")

    assert resposta.status_code == 422
    assert "PDF" in resposta.json()["detail"]


def test_pdf_sem_texto_resulta_em_422(cliente: TestClient) -> None:
    resposta = _enviar(cliente, "/pdf/resumo", pdf_em_branco())

    assert resposta.status_code == 422


def test_arquivo_grande_demais_resulta_em_413(cliente: TestClient) -> None:
    resposta = _enviar(cliente, "/pdf/resumo", b"\x00" * (11 * 1024 * 1024))

    assert resposta.status_code == 413


def test_falha_do_modelo_resulta_em_502(cliente: TestClient, gerador_fake: GeradorFake) -> None:
    gerador_fake.erro = ErroDoModelo("Falha ao consultar o modelo")

    resposta = _enviar(cliente, "/pdf/resumo", PDF)

    assert resposta.status_code == 502


def test_flashcards_com_resposta_inutilizavel_resulta_em_502(
    cliente: TestClient, gerador_fake: GeradorFake
) -> None:
    gerador_fake.resposta = "Nao consegui gerar os flashcards."

    resposta = _enviar(cliente, "/pdf/flashcards", PDF)

    assert resposta.status_code == 502


def test_raiz_confirma_que_o_servico_esta_no_ar(cliente: TestClient) -> None:
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["documentacao"] == "/docs"


def test_raiz_informa_o_modelo_configurado(cliente: TestClient) -> None:
    """O modelo aparece na raiz para que o deploy seja conferível sem enviar arquivo."""
    assert cliente.get("/").json()["modelo"] == "meta/llama-3.1-8b-instruct"


def test_raiz_nao_expoe_a_chave_de_api(cliente: TestClient) -> None:
    assert "chave-de-teste" not in cliente.get("/").text


def test_openapi_expoe_as_rotas_com_schema_de_resposta(cliente: TestClient) -> None:
    esquema = cliente.get("/openapi.json").json()

    assert set(esquema["paths"]) == {"/", "/pdf/resumo", "/pdf/flashcards"}
    conteudo = esquema["paths"]["/pdf/flashcards"]["post"]["responses"]["200"]["content"]
    assert "RespostaFlashcards" in conteudo["application/json"]["schema"]["$ref"]
