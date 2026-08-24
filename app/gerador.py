"""Contrato para geração de texto por um modelo de linguagem."""

from abc import ABC, abstractmethod


class GeradorDeTexto(ABC):
    """Interface para qualquer provedor de modelo de linguagem.

    As rotas dependem desta abstração, e não de um provedor concreto: trocar o
    NVIDIA NIM por outro serviço (ou por um dublê nos testes) é escrever uma
    nova subclasse, sem alterar nenhum endpoint.
    """

    @abstractmethod
    def gerar(self, prompt: str) -> str:
        """Devolve a resposta do modelo para `prompt`.

        Implementações devem levantar `ErroDoModelo` quando não conseguirem
        obter uma resposta utilizável.
        """
