from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    
    nome = Column(String, nullable=False)
    
    email = Column(String, unique=True, nullable=False)
    
    senha = Column(String, nullable=False)

    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")


class TipoTransacao(str, Enum):
    RECEITA = 'RECEITA'
    DESPESA = 'DESPESA'

class Categoria(str, Enum):
    
    #despesas
    MERCADO = 'MERCADO'
    ALIMENTACAO = 'ALIMENTACAO'
    TRANSPORTE = 'TRANSPORTE'
    SAUDE = 'SAUDE'
    LAZER = 'LAZER'
    ASSINATURAS = 'ASSINATURAS'
    MORADIA = 'MORADIA'
    CONTAS = 'CONTAS'
    PARCELAS = 'PARCELAS'
    
    #receitas
    SALARIO = 'SALARIO'
    FREELANCE = 'FREELANCE'
    REEMBOLSO = 'REEMBOLSO'
    INVESTIMENTOS = 'INVESTIMENTOS'
    VENDA = 'VENDA'
    BONUS = 'BONUS'
    
    #ambos os tipos
    PRESENTE = 'PRESENTE'
    OUTROS = 'OUTROS'


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)

    descricao = Column(String(255), nullable=True)

    valor = Column(Float, nullable=False)

    tipo = Column(SQLEnum(TipoTransacao), nullable=False)

    categoria = Column(SQLEnum(Categoria), nullable=False)

    data = Column(DateTime, nullable=False, server_default=func.now())

    created_at = Column(DateTime,server_default=func.now())

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="transacoes")


   

