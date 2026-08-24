"""Provedores de dependências injetadas nas rotas.

Nos testes, `app.dependency_overrides` substitui `obter_gerador` por um dublê,
o que permite exercitar os endpoints sem rede e sem chave de API.
"""

from functools import lru_cache

from fastapi import Depends

from app.config import Configuracao, obter_configuracao
from app.extracao import ExtratorPDF
from app.gerador import GeradorDeTexto
from app.gerador_nim import GeradorNIM


@lru_cache
def _construir_extrator(max_paginas: int, max_mb: int) -> ExtratorPDF:
    return ExtratorPDF(max_paginas=max_paginas, max_mb=max_mb)


@lru_cache
def _construir_gerador(api_key: str, base_url: str, modelo: str) -> GeradorNIM:
    return GeradorNIM(api_key=api_key, base_url=base_url, modelo=modelo)


def obter_extrator(config: Configuracao = Depends(obter_configuracao)) -> ExtratorPDF:
    """Extrator configurado com os limites vindos do ambiente."""
    return _construir_extrator(config.max_paginas, config.max_mb)


def obter_gerador(config: Configuracao = Depends(obter_configuracao)) -> GeradorDeTexto:
    """Gerador de texto usado em produção (NVIDIA NIM)."""
    return _construir_gerador(config.nvidia_api_key, config.nim_base_url, config.nim_model)
