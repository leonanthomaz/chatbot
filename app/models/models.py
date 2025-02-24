# app/models/models.py

from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from typing import List, Optional

# Modelo de entrada para a API de chat
class MessageRequest(BaseModel):
    message: str

class Empresa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    cnpj: str
    telefone: str
    endereco: str
    tipo: str
    produtos: List["Produto"] = Relationship(back_populates="empresa")
    servicos: List["Servico"] = Relationship(back_populates="empresa")

class Produto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    preco: float
    categoria: str
    estoque: int
    imagem: str
    empresa_id: int = Field(foreign_key="empresa.id")
    empresa: Optional[Empresa] = Relationship(back_populates="produtos")
    codigo: str

class ProdutoRequest(BaseModel):
    nome: str
    descricao: str
    preco: float
    categoria: str
    estoque: int
    imagem: str
    empresa_id: int
    codigo: str
    
class Servico(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    descricao: str
    preco: float
    categoria: str
    imagem: str
    empresa_id: int = Field(foreign_key="empresa.id")
    empresa: Optional[Empresa] = Relationship(back_populates="servicos")
    codigo: str

class ServicoRequest(BaseModel):
    nome: str
    descricao: str
    preco: float
    categoria: str
    imagem: str
    empresa_id: int
    codigo: str