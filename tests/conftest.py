"""Fixtures compartilhadas.

A suíte inteira roda offline: a configuração recebe uma chave fictícia e o
`GeradorDeTexto` real é substituído por um dublê via `dependency_overrides`.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import obter_configuracao
from app.dependencias import obter_gerador
from tests.apoio import GeradorFake


@pytest.fixture
def gerador_fake() -> GeradorFake:
    return GeradorFake()


@pytest.fixture
def cliente(monkeypatch: pytest.MonkeyPatch, gerador_fake: GeradorFake) -> TestClient:
    monkeypatch.setenv("NVIDIA_API_KEY", "chave-de-teste")
    # A configuração é cacheada por processo; limpar antes e depois evita que um
    # teste enxergue o ambiente montado por outro.
    obter_configuracao.cache_clear()

    from app.main import criar_app

    app = criar_app()
    app.dependency_overrides[obter_gerador] = lambda: gerador_fake

    yield TestClient(app)

    obter_configuracao.cache_clear()
