# app/gateway/mock_provider.py

import json
import os
from app.gateway.ia_provider import IAProvider

class MockProvider(IAProvider):
    """Provedor de IA mockado para testes."""

    def __init__(self, mock_file="app/config/mock_responses.json"):
        self.mock_file = mock_file
        self.responses = self._load_mock_responses()

    def _load_mock_responses(self):
        if os.path.exists(self.mock_file):
            with open(self.mock_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def gerar_resposta(self, produtos: list, servicos: list, mensagem: str) -> str:
        return self.responses.get(mensagem, "Mock: Desculpe, não tenho uma resposta para essa pergunta.")


