# app/gateway/provider_factory.py

from app.config.settings import Configuration
from app.gateway.ia_provider import IAProvider

from app.api.deepseek_api import DeepSeekProvider
from app.api.gemini_api import GeminiProvider
from app.api.openai_api import OpenAIProvider

from app.gateway.mock_provider import MockProvider

import logging

config = Configuration()

def get_ia_provider() -> IAProvider:
    """Retorna a instância do provedor de IA configurado."""
    
    if config.ia_provider == "mock":
        logging.info("Usando MockProvider para respostas de IA.")
        return MockProvider()

    provider = config.ia_provider
    logging.info(f"Inteligência Artificial escolhida: {provider}")

    if provider == "gemini":
        return GeminiProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        return DeepSeekProvider()

