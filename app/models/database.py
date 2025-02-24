# app/models/database.py

import os
import json
import logging
from sqlmodel import SQLModel, Session, create_engine, select
from app.models.models import Empresa, Produto, Servico  # Importando a classe Servico

# Configuração do logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DatabaseManager:
    def __init__(self, db_name="workana.db", json_path="dados_empresa.json", environment="development"):
        self.db_name = db_name
        self.json_path = json_path
        self.environment = environment
        self.engine = create_engine(f"sqlite:///{self.db_name}", echo=False)
        logging.info("DatabaseManager inicializado com banco de dados: %s", self.db_name)

    def create_tables(self):
        """Cria as tabelas no banco de dados."""
        SQLModel.metadata.create_all(self.engine)
        logging.info("Tabelas criadas no banco de dados.")

    def database_exists(self):
        """Verifica se o banco de dados já existe."""
        exists = os.path.exists(self.db_name)
        logging.info("Verificação do banco de dados: %s", "Existe" if exists else "Não existe")
        return exists

    def populate_database(self):
        """Popula o banco de dados baseado no ambiente."""
        if self.environment == "production":
            logging.info("Modo produção detectado. O banco de dados não será populado.")
            return

        with Session(self.engine) as session:
            # Contagem dos produtos no banco
            count = session.exec(select(Produto)).all()
            if not count:
                logging.info("Nenhum produto encontrado no banco. Populando...")
                empresa = self.load_empresa_from_json() if self.environment == "test" else self.get_default_empresa()
                if not empresa and self.environment == "test":
                    empresa = self.get_default_empresa()
                session.add(empresa)
                session.commit()
                logging.info("Banco de dados populado com %d produtos.", len(empresa.produtos))
            else:
                logging.info("Banco de dados já possui produtos. Nenhuma ação necessária.")

    def load_empresa_from_json(self):
        """Carrega a empresa e seus produtos de um arquivo JSON."""
        if os.path.exists(self.json_path):
            logging.info("Carregando empresa do arquivo JSON: %s", self.json_path)
            with open(self.json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            empresa_data = data["empresa"]
            produtos_data = empresa_data.pop("produtos", [])
            servicos_data = empresa_data.pop("servicos", [])  # Carregar os serviços

            empresa = Empresa(
                nome=empresa_data["nome"],
                descricao=empresa_data["descricao"],
                cnpj=empresa_data["cnpj"],
                telefone=empresa_data["telefone"],
                endereco=empresa_data["endereco"],
                tipo=empresa_data["tipo"]  # Tipo da empresa
            )

            produtos = [
                Produto(
                    nome=p["nome"],
                    preco=p["preco"],
                    descricao=p["descricao"],
                    categoria=p["categoria"],
                    estoque=p["estoque"],
                    imagem=p["imagem"],
                    codigo=p["codigo"],
                    empresa=empresa
                ) for p in produtos_data
            ]

            servicos = [
                Servico(
                    nome=s["nome"],
                    descricao=s["descricao"],
                    categoria=s["categoria"],
                    preco=s["preco"],
                    imagem=s["imagem"],
                    empresa=empresa
                ) for s in servicos_data
            ]

            empresa.produtos = produtos
            empresa.servicos = servicos
            return empresa
        logging.warning("Arquivo JSON não encontrado. Nenhuma empresa será carregada.")
        return None

    def get_default_empresa(self):
        """Retorna uma empresa padrão caso o JSON não exista."""
        logging.info("Utilizando empresa padrão para popular o banco.")
        empresa = Empresa(
            nome="Loja Exemplo",
            descricao="Loja de exemplo para testar o sistema.",
            cnpj="00.000.000/0001-00",
            telefone="(11) 0000-0000",
            endereco="Rua Exemplo, 100, São Paulo, SP",
            tipo="produtos_servicos"
        )
        produtos = [
            Produto(
                nome="Camiseta",
                preco=19.99,
                descricao="Camiseta de algodão, confortável e durável.",
                categoria="Roupas",
                estoque=50,
                imagem="https://example.com/camiseta.jpg",
                codigo="CAM123",
                empresa=empresa
            ),
            Produto(
                nome="Notebook",
                preco=149.99,
                descricao="Notebook ultra-rápido, com 16GB de RAM.",
                categoria="Eletrônicos",
                estoque=30,
                imagem="https://example.com/notebook.jpg",
                codigo="NB456",
                empresa=empresa
            ),
            Produto(
                nome="Caneca",
                preco=9.99,
                descricao="Caneca térmica, mantém a bebida quente por horas.",
                categoria="Utilidades",
                estoque=100,
                imagem="https://example.com/caneca.jpg",
                codigo="CAN789",
                empresa=empresa
            )
        ]

        servicos = [
            Servico(
                nome="Consultoria",
                descricao="Consultoria especializada em produtos de informática.",
                preco=200.00,
                categoria="Consultoria",
                imagem="https://example.com/consultoria.jpg",
                empresa=empresa,
                codigo="CONS001" #codigo adicionado
            ),
            Servico(
                nome="Suporte Técnico",
                descricao="Suporte técnico para computadores e dispositivos móveis.",
                preco=150.00,
                imagem="https://example.com/consultoria.jpg",
                categoria="Suporte",
                empresa=empresa,
                codigo="SUP002" #codigo adicionado
            )
        ]
        empresa.produtos = produtos
        empresa.servicos = servicos  # Adicionando serviços à empresa padrão
        return empresa

    def get_empresa_info(self):
        """Retorna informações da empresa com seus produtos e serviços associados."""
        with Session(self.engine) as session:
            empresa = session.exec(select(Empresa).limit(1)).first()
            if empresa:
                produtos = [p.nome for p in empresa.produtos]
                servicos = [s.nome for s in empresa.servicos]
                return {
                    "nome": empresa.nome,
                    "descricao": empresa.descricao,
                    "cnpj": empresa.cnpj,
                    "telefone": empresa.telefone,
                    "endereco": empresa.endereco,
                    "tipo": empresa.tipo,
                    "produtos": produtos,
                    "servicos": servicos
                }
                
            return None

# Exportando o engine para ser importado onde for necessário
engine = DatabaseManager().engine
