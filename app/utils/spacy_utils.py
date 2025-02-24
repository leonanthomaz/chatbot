# app/utils/spacy_utils.py

import spacy
import logging
from app.exceptions.spacy_error import SpacyModelLoadError, SpacyProcessingError

class SpacyProcessor:
    def __init__(self, modelo="pt_core_news_sm"):
        """
        Inicializa o processador spaCy.

        Args:
            modelo (str): Nome do modelo spaCy a ser carregado.
        """
        try:
            self.nlp = spacy.load(modelo)
        except OSError as e:
            logging.error(f"Erro ao carregar o modelo spaCy: {e}")
            raise SpacyModelLoadError(f"Não foi possível carregar o modelo spaCy '{modelo}': {e}")

        self.SINONIMOS = {
            "celular": "smartphone",
            "camisa": "camiseta",
            "telefone": "smartphone",
            "computador": "notebook",
            "laptop": "notebook",
            "pc": "notebook",
            "tv": "televisão"
        }

    def processar_mensagem(self, mensagem):
        """
        Processa a mensagem para extrair palavras-chave relevantes.

        Args:
            mensagem (str): Mensagem a ser processada.

        Returns:
            list: Lista de palavras-chave extraídas.
        """
        if self.nlp is None:
            logging.error("Modelo spaCy não carregado. Não é possível processar a mensagem.")
            raise SpacyModelLoadError("Modelo spaCy não carregado.")

        try:
            doc = self.nlp(mensagem)
            palavras_chave = []
            palavras_irrelevantes = ["preciso", "quero", "gostaria", "de", "estou", "vou", "em", "para", "a", "o", "na", "nao"]
            substantivos_irrelevantes = ["casa", "ontem", "hoje"]

            for token in doc:
                # Otimização: Verificação de POS e lematização em uma única iteração
                if token.pos_ in ["NOUN", "PROPN"]:
                    lemma = token.lemma_.lower()  # Lematização para reduzir variações
                    palavra_normalizada = self.SINONIMOS.get(lemma, token.text) # normalização com lema ou palavra original
                    if (palavra_normalizada.lower() not in palavras_irrelevantes and
                        palavra_normalizada.lower() not in substantivos_irrelevantes):
                        palavras_chave.append(palavra_normalizada)

            return palavras_chave
        except Exception as e:
            logging.error(f"Erro ao processar a mensagem com spaCy: {e}")
            raise SpacyProcessingError(f"Erro ao processar a mensagem: {e}")