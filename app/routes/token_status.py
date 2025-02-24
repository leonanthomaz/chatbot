# app/routes/token_status.py

import os
import requests
import logging
from fastapi import APIRouter

class TokenStatusRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.add_api_route("/check_token_status", self.check_token_status, methods=["GET"])

    def check_openai_status(self, api_key):
        url = "https://openrouter.ai/api/v1/auth/key"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        try:
            logging.info("Fazendo requisição para o OpenAI")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            logging.info(f"Status da resposta do OpenAI: {response.status_code}")

            data = response.json()
            key_info = data.get("data", {})

            logging.info(f"Créditos usados: {key_info.get('usage')}, Limite de créditos: {key_info.get('limit')}")

            return {
                "provider": "OpenAI",
                "label": key_info.get("label"),
                "credits_used": key_info.get("usage"),
                "credit_limit": key_info.get("limit"),
                "is_free_tier": key_info.get("is_free_tier"),
                "rate_limit_requests": key_info["rate_limit"]["requests"],
                "rate_limit_interval": key_info["rate_limit"]["interval"]
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar OpenAI: {e}")
            return {"error": f"Erro ao acessar OpenAI: {e}"}

    def check_deepseek_status(self, api_key):
        url = "https://api.deepseek.com/v1/status"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        try:
            logging.info("Fazendo requisição para o DeepSeek")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            logging.info(f"Status da resposta do DeepSeek: {response.status_code}")

            data = response.json()

            logging.info(f"Créditos usados: {data.get('usage', {}).get('used', 0)}, Limite de créditos: {data.get('usage', {}).get('limit', 0)}")

            return {
                "provider": "DeepSeek",
                "credits_used": data.get("usage", {}).get("used", 0),
                "credit_limit": data.get("usage", {}).get("limit", 0),
                "rate_limit_requests": data.get("rate_limit", {}).get("requests", 0),
                "rate_limit_interval": data.get("rate_limit", {}).get("interval", "N/A")
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar DeepSeek: {e}")
            return {"error": f"Erro ao acessar DeepSeek: {e}"}

    async def check_token_status(self, provider: str):
        logging.info(f"Verificando status do token para o provedor: {provider}")

        # Verifica qual provedor está sendo solicitado
        if provider.lower() == 'openai' and self.openai_api_key:
            result = self.check_openai_status(self.openai_api_key)
            logging.info("Resultado da verificação do OpenAI")
        elif provider.lower() == 'deepseek' and self.deepseek_api_key:
            result = self.check_deepseek_status(self.deepseek_api_key)
            logging.info("Resultado da verificação do DeepSeek")
        else:
            result = {"error": "Provedor inválido ou chave não configurada corretamente."}
            logging.error("Provedor inválido ou chave não configurada corretamente.")

        return result