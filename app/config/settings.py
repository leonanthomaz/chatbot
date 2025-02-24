# app/config/config.py

import os
import redis

class Configuration:
    def __init__(self):
        # Carrega as variáveis de ambiente
        self.ia_provider = os.getenv("IA_PROVIDER", "mock").lower()
        self.assistant_name = os.getenv("ASSISTANT_NAME")
        
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = "https://openrouter.ai/api/v1"

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = "https://openrouter.ai/api/v1"

        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

    def get_redis_client(self):
        """Retorna uma instância do cliente Redis configurado."""
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),  # Servidor Redis local
            port=int(os.getenv("REDIS_PORT", 6379)),  # Porta padrão do Redis
            db=int(os.getenv("REDIS_DB", 0)),  # Banco de dados 0
            decode_responses=True  # Retorna strings em vez de bytes
        )

