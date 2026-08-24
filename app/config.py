"""Configuração da aplicação, lida do ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    """Parâmetros de execução.

    `nvidia_api_key` não tem valor padrão de propósito: sem ela a aplicação não
    sobe, evitando um container silenciosamente mal configurado.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nvidia_api_key: str
    nim_base_url: str = "https://integrate.api.nvidia.com/v1"
    nim_model: str = "meta/llama-3.1-8b-instruct"
    max_paginas: int = 30
    max_mb: int = 10


@lru_cache
def obter_configuracao() -> Configuracao:
    """Devolve a configuração única do processo (cacheada entre requisições)."""
    return Configuracao()
