# app/api/gemini_api.py

import google.generativeai as genai
from app.gateway.ia_provider import IAProvider
from app.config.settings import Configuration
import logging

config = Configuration()

class GeminiProvider(IAProvider):
    """Implementação do Gemini como provedor de IA."""

    def __init__(self):
        api_key = config.gemini_api_key
        self.assistant_name = config.assistant_name
        if not api_key:
            raise ValueError("GEMINI_API_KEY não está configurada no ambiente.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def gerar_resposta(self, produtos: list, servicos: list, mensagem: str) -> str:
        try:
            logging.info(f"Enviando mensagem para Gemini: {mensagem}")

            # Instruções de sistema para orientar o comportamento do Gemini
            prompt_inicial = f"""
            Você é um assistente de vendas especializado chamado {self.assistant_name}. 
            Sua função é fornecer respostas objetivas e precisas sobre os produtos ({produtos}) e serviços ({servicos}) da empresa. 
            Responda de forma direta e objetiva, sempre em português do Brasil.
            Não faça perguntas ao usuário. Forneça as informações que lhe competem com firmeza e precisão.
            Se o usuário perguntar sobre algo que não é vendido pela empresa, informe de forma clara que não trabalhamos com esse item.
            Evite respostas genéricas, como "sou um modelo de linguagem treinado" ou semelhantes.
            Responda de forma direta, sem divagações desnecessárias.
            """

            # Gerar resposta com base no prompt
            response = self.model.generate_content(f"{prompt_inicial}\nPergunta do usuário: {mensagem}")

            if response and hasattr(response, "text"):
                return response.text.strip()

            logging.error("Resposta vazia ou inesperada do Gemini.")
            return "Erro: Resposta não gerada."

        except Exception as e:
            logging.exception("Erro ao chamar Gemini API")
            return f"Erro ao gerar resposta com Gemini: {str(e)}"