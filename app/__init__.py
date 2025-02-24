# app/__init__.py

import os
import logging
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from .routes.chat import ChatRouter
from .routes.token_status import TokenStatusRouter
from .routes.empresa import EmpresaRouter
from .routes.produto import ProdutoRouter
from .routes.servico import ServicoRouter

from app.models.database import DatabaseManager

def create_app():
    """
    Cria e configura a aplicação FastAPI, incluindo middlewares e rotas.
    Também gerencia a criação/população do banco de dados conforme o ambiente.
    """
    app = FastAPI()

    # Configuração de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configuração de logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Carrega as variáveis de ambiente
    load_dotenv(dotenv_path=".env")

    # Define o ambiente
    ambiente = os.getenv("ENVIRONMENT", "development")

    # Gerenciador do banco de dados
    db_manager = DatabaseManager(environment=ambiente)

    if ambiente in ["test", "development"]:
        logging.info(f"Ambiente {ambiente} detectado. Configurando banco de dados...")
        db_manager.create_tables()
        db_manager.populate_database()
    elif ambiente == "production":
        logging.info("Ambiente de produção detectado. Apenas verificando a existência do banco de dados.")
        if not db_manager.database_exists():
            db_manager.create_tables()

    # Inclui as rotas
    app.include_router(ChatRouter())
    app.include_router(TokenStatusRouter())
    app.include_router(EmpresaRouter())
    app.include_router(ProdutoRouter())
    app.include_router(ServicoRouter())

    return app