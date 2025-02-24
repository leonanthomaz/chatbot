# app/api/openai_api.py

from openai import OpenAI
from app.gateway.ia_provider import IAProvider
from app.config.settings import Configuration
import logging

config = Configuration()

class OpenAIProvider(IAProvider):
    """Implementação do Openai como provedor de IA."""

    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key, base_url=config.openai_base_url)
        self.assistant_name = config.assistant_name

    def gerar_resposta(self, produtos: list, servicos: list, mensagem: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content":
                        f"Você é um assistente de vendas experiente e confiável. Seu nome é {self.assistant_name}. Responda de forma direta e objetiva, sempre em português do Brasil.\n"
                        f"Se o usuário perguntar sobre produtos, consulte a base de produtos {produtos} e informe os preços e descrições.\n"
                        f"Se o usuário perguntar sobre serviços, consulte a base de serviços {servicos} e forneça detalhes.\n"
                        "Não se comporte como uma estagiária. Receba a pergunta, processe e envie a resposta com firmeza. O usuário é seu cliente.\n"
                        "Se um produto ou serviço não estiver na base, diga que não trabalhamos com ele.\n"
                        "Evite respostas genéricas ou repetição desnecessária.\n"
                        "Não invente produtos e serviços, e não mencione exemplos que não correspondam aos produtos e serviços disponíveis."},
                    {"role": "user", "content": mensagem}
                ],
                stream=False,
            )

            return response.choices[0].message.content[:200] if response.choices else "Resposta não gerada."

        except Exception as e:
            logging.error(f"Erro ao processar IA da Openai: {e}")
            return "Erro ao gerar resposta com Openai."

