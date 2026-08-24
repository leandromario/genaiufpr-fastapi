"""Implementação de `GeradorDeTexto` sobre o catálogo NVIDIA NIM."""

from openai import OpenAI, OpenAIError

from app.excecoes import ErroDoModelo
from app.gerador import GeradorDeTexto


class GeradorNIM(GeradorDeTexto):
    """Gera texto com um modelo hospedado em build.nvidia.com.

    O NIM expõe uma API compatível com a da OpenAI, por isso o cliente `openai`
    é reaproveitado apenas com outra `base_url`.
    """

    def __init__(self, api_key: str, base_url: str, modelo: str) -> None:
        self._cliente = OpenAI(base_url=base_url, api_key=api_key)
        self._modelo = modelo

    def gerar(self, prompt: str) -> str:
        try:
            resposta = self._cliente.chat.completions.create(
                model=self._modelo,
                messages=[{"role": "user", "content": prompt}],
            )
        except OpenAIError as erro:
            raise ErroDoModelo(f"Falha ao consultar o modelo {self._modelo}: {erro}") from erro

        conteudo = resposta.choices[0].message.content
        if not conteudo:
            raise ErroDoModelo("O modelo retornou uma resposta vazia")
        return conteudo
