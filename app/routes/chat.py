# app/routes/chat.py

from fastapi import APIRouter, HTTPException
from app.models.models import MessageRequest
from app.models.database import DatabaseManager
from app.utils.spacy_utils import SpacyProcessor
from app.utils.redis_utils import RedisCache
from app.gateway.provider_factory import get_ia_provider
import logging

class ChatRouter(APIRouter):
    """
    Roteador de chat responsável por gerenciar interações com o usuário,
    consultando FAQs, informações da empresa e um provedor de IA.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_cache = RedisCache()
        self.database_manager = DatabaseManager()
        self.spacy_processor = SpacyProcessor()
        self.faq = {
            "politica de troca": "Nossa política de troca permite devoluções em até 30 dias. Para mais detalhes, acesse nosso site.",
            "trocas": "Nossa política de troca permite devoluções em até 30 dias. Para mais detalhes, acesse nosso site.",
            "devoluções": "Nossa política de troca permite devoluções em até 30 dias. Para mais detalhes, acesse nosso site.",
            "entrega rj": "Sim, fazemos entregas para o Rio de Janeiro. Consulte o frete na finalização da compra.",
            "entregas rio de janeiro": "Sim, fazemos entregas para o Rio de Janeiro. Consulte o frete na finalização da compra."
        }
        self.resposta_generica = "Desculpe, não entendi sua pergunta. Por favor, entre em contato com nosso suporte."
        self.add_api_route("/chat", self.chat, methods=["POST"])

    async def chat(self, request: MessageRequest):
        """
        Rota principal de interação do chat.

        Verifica cache, responde perguntas frequentes, busca informações da empresa
        e consulta provedor de IA se necessário.

        Args:
            request (MessageRequest): Objeto contendo a mensagem do usuário.

        Returns:
            dict: Resposta formatada para o usuário.
        """
        logging.info(f"Recebendo mensagem: {request.message}")

        # Verifica se existe uma resposta em cache
        cached_response = self.redis_cache.get_cached_response(request.message)
        if cached_response:
            return {"response": cached_response}

        # Processa a mensagem para identificar palavras-chave
        palavras_chave = self.spacy_processor.processar_mensagem(request.message)
        logging.info(f"Palavras-chave identificadas: {palavras_chave}")

        # Verifica se a mensagem contém palavras-chave do FAQ
        for chave, resposta in self.faq.items():
            if chave in request.message.lower():
                self.redis_cache.cache_response(request.message, resposta)
                return {"response": resposta}

        # Busca informações da empresa no banco de dados
        empresa_info = self.database_manager.get_empresa_info()
        if not empresa_info:
            logging.warning("Nenhuma informação de empresa encontrada.")
            return {"response": self.resposta_generica}

        tipo_empresa = empresa_info.get("tipo", "")
        itens_encontrados = self._buscar_itens(palavras_chave, empresa_info, tipo_empresa)

        if itens_encontrados:
            resposta_final = self._formatar_resposta(itens_encontrados, tipo_empresa)
            self.redis_cache.cache_response(request.message, resposta_final)
            return {"response": resposta_final}

        # Caso não encontre itens, consulta a IA
        return await self._consultar_ia(request.message)

    def _buscar_itens(self, palavras_chave, empresa_info, tipo_empresa):
        """
        Busca produtos ou serviços com base nas palavras-chave identificadas.

        Args:
            palavras_chave (list): Lista de palavras-chave extraídas da mensagem.
            empresa_info (dict): Informações da empresa, incluindo produtos e serviços.
            tipo_empresa (str): Tipo da empresa ('produtos', 'servicos', 'produtos_servicos').

        Returns:
            list: Lista de itens encontrados (produtos ou serviços).
        """
        itens = []
        if tipo_empresa in ["produtos", "produtos_servicos"]:
            itens.extend([p for p in empresa_info.get("produtos", []) if p.lower() in palavras_chave])
        if tipo_empresa in ["servicos", "produtos_servicos"]:
            itens.extend([s for s in empresa_info.get("servicos", []) if s.lower() in palavras_chave])
        return itens

    def _formatar_resposta(self, itens, tipo_empresa):
        """
        Formata a resposta para o usuário com os itens encontrados.

        Args:
            itens (list): Lista de itens (produtos ou serviços).
            tipo_empresa (str): Tipo da empresa.

        Returns:
            str: Resposta formatada.
        """
        categoria = "produtos e serviços" if tipo_empresa == "produtos_servicos" else tipo_empresa
        resposta = f"Aqui estão os {categoria} disponíveis:\n"
        resposta += "\n".join(f"- {item}" for item in itens)
        return resposta

    async def _consultar_ia(self, mensagem):
        """
        Consulta o provedor de IA para gerar uma resposta personalizada.

        Args:
            mensagem (str): Mensagem do usuário.

        Returns:
            dict: Resposta gerada pelo provedor de IA.
        """
        empresa_info = self.database_manager.get_empresa_info()
        produtos = empresa_info.get("produtos", [])
        servicos = empresa_info.get("servicos", [])
        
        ia_provider = get_ia_provider()
        try:
            resposta_ia = ia_provider.gerar_resposta(produtos, servicos, mensagem)
            logging.info(f"Resposta final da Assistente: {resposta_ia}")
            self.redis_cache.cache_response(mensagem, resposta_ia)
            return {"response": resposta_ia}
        except Exception as e:
            logging.error(f"Erro ao consultar o provedor de IA: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar a mensagem com IA.")
