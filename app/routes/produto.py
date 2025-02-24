# app/routes/produto.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.models import Produto, ProdutoRequest
from app.models.database import engine

class ProdutoRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/produtos/", self.create_produto, methods=["POST"])
        self.add_api_route("/produtos/", self.list_produtos, methods=["GET"])

    def get_session(self):
        """Função para criar e obter uma sessão de banco de dados"""
        with Session(engine) as session:
            yield session  # Retorna a sessão que será usada nas rotas

    async def create_produto(self, produto: ProdutoRequest, session: Session = Depends(get_session)):
        """
        Cria um novo produto no banco de dados.

        **Entrada:**
        - produto (ProdutoRequest): Dados do produto para cadastro.

        **Saída:**
        - Produto: Objeto do produto cadastrado com os dados retornados do banco.
        """
        # Criação de um produto a partir da solicitação recebida
        produto_db = Produto(**produto.dict())
        # Adicionando o produto no banco de dados
        session.add(produto_db)
        session.commit()  # Confirmando a transação no banco
        session.refresh(produto_db)  # Atualizando o produto com os dados do banco
        return produto_db  # Retorna o produto que foi criado

    async def list_produtos(self, session: Session = Depends(get_session)):
        """
        Retorna a lista de todos os produtos cadastrados.

        **Entrada:**
        - Nenhuma.

        **Saída:**
        - List[Produto]: Lista de todos os produtos no banco.
        """
        # Executa a consulta para pegar todos os produtos
        produtos = session.exec(select(Produto)).all()
        return produtos  # Retorna a lista de produtos