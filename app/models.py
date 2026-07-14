from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base  
from enum import Enum

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String, nullable=False)
    
    email = Column(String, unique=True, nullable=False)
    
    senha = Column(String, nullable=False)

class TipoTransacao(str, Enum):

    RECEITA = 'RECEITA'
    DESPESA = 'DESPESA'

class CategoriaDespesa(str, Enum):
    
    MERCADO = 'MERCADO'
    ALIMENTACAO = 'ALIMENTACAO'
    TRANSPORTE = 'TRANSPORTE'
    SAUDE = 'SAUDE'
    LAZER = 'LAZER'
    ASSINATURAS = 'ASSINATURAS'
    MORADIA = 'MORADIA'
    CONTAS = 'CONTAS'
    PARCELAS = 'PARCELAS'
    OUTROS = 'OUTROS'

class CategoriaReceita(str, Enum):

    SALARIO = 'SALARIO'
    FREELANCE = 'FREELANCE'
    REEMBOLSO = 'REEMBOLSO'
    INVESTIMENTOS = 'INVESTIMENTOS'
    VENDA = 'VENDA'
    BONUS = 'BONUS'
    PRESENTE = 'PRESENTE'
    OUTROS = 'OUTROS'