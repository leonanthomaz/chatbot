# app/routes/empresa.py

from fastapi import APIRouter
from sqlmodel import Session, select
from app.models.models import Empresa
from app.models.database import engine

class EmpresaRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/empresa", self.criar_empresa, methods=["POST"])
        self.add_api_route("/empresa", self.obter_empresa, methods=["GET"])

    def criar_empresa(self, empresa: Empresa):
        """
        Cria uma nova empresa no banco de dados.

        **Entrada:**
        - empresa (Empresa): Dados da empresa a ser cadastrada.

        **Saída:**
        - message (str): Mensagem de sucesso.
        - empresa (Empresa): Dados da empresa que foi criada.
        """
        # Criação da sessão de banco de dados
        with Session(engine) as session:
            session.add(empresa)  # Adiciona a empresa à sessão
            session.commit()  # Confirma a transação no banco
            session.refresh(empresa)  # Atualiza a empresa com dados do banco
            return {"message": "Empresa criada com sucesso!", "empresa": empresa}  # Retorna a mensagem de sucesso e os dados da empresa criada

    def obter_empresa(self):
        """
        Retorna os dados da empresa cadastrada.

        **Entrada:**
        - Nenhuma.

        **Saída:**
        - empresa (Empresa ou dict): Dados da empresa cadastrada ou mensagem indicando que nenhuma empresa foi cadastrada.
        """
        # Criação da sessão de banco de dados
        with Session(engine) as session:
            statement = select(Empresa)  # Define a consulta para selecionar a empresa
            empresa = session.exec(statement).first()  # Executa a consulta e pega o primeiro registro
            # Retorna a empresa ou uma mensagem caso não exista
            return empresa or {"message": "Nenhuma empresa cadastrada"}