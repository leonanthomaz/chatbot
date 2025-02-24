# app/gateway/ia_provider.py

from abc import ABC, abstractmethod

class IAProvider(ABC):
    """Interface para diferentes provedores de IA."""

    @abstractmethod
    def gerar_resposta(self, produtos: list, servicos: list, mensagem: str) -> str:
        pass
    

class IAProviderExemplo(IAProvider):
    """Implementação exemplo do provedor de IA."""

    def gerar_resposta(self, mensagem: str) -> str:
        return f"Resposta gerada para: {mensagem}"