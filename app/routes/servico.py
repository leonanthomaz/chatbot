from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.models import Servico, ServicoRequest
from app.models.database import engine

class ServicoRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/servicos/", self.create_servico, methods=["POST"])
        self.add_api_route("/servicos/", self.list_servicos, methods=["GET"])

    def get_session(self):
        """Função para criar e obter uma sessão de banco de dados"""
        with Session(engine) as session:
            yield session  # Retorna a sessão que será usada nas rotas

    async def create_servico(self, servico: ServicoRequest, session: Session = Depends(get_session)):
        """
        Cria um novo serviço no banco de dados.

        **Entrada:**
        - servico (ServicoRequest): Dados do serviço para cadastro.

        **Saída:**
        - Servico: Objeto do serviço cadastrado com os dados retornados do banco.
        """
        # Criação de um serviço a partir da solicitação recebida
        servico_db = Servico(**servico.dict())
        # Adicionando o serviço no banco de dados
        session.add(servico_db)
        session.commit()  # Confirmando a transação no banco
        session.refresh(servico_db)  # Atualizando o serviço com os dados do banco
        return servico_db  # Retorna o serviço que foi criado

    async def list_servicos(self, session: Session = Depends(get_session)):
        """
        Retorna a lista de todos os serviços cadastrados.

        **Entrada:**
        - Nenhuma.

        **Saída:**
        - List[Servico]: Lista de todos os serviços no banco.
        """
        # Executa a consulta para pegar todos os serviços
        servicos = session.exec(select(Servico)).all()
        return servicos  # Retorna a lista de serviços