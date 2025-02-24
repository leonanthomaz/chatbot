# tests/test_ia_provider.py
from app.utils.ia_provider import IAProviderExemplo

def test_gerar_resposta():
    provedor = IAProviderExemplo()
    mensagem = "Olá, IA!"
    resposta = provedor.gerar_resposta(mensagem)
    assert resposta == "Resposta gerada para: Olá, IA!"
