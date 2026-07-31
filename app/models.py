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
    investimentos = relationship("PosicaoInvestimento", back_populates="usuario")


class TipoTransacao(str, Enum):
    RECEITA = 'RECEITA'
    DESPESA = 'DESPESA'

#Decidi usar uma classe Enum em vez de duas pois facilita a validação
class Categoria(str, Enum):
    
    #Despesas
    MERCADO = 'MERCADO'
    ALIMENTACAO = 'ALIMENTACAO'
    TRANSPORTE = 'TRANSPORTE'
    SAUDE = 'SAUDE'
    LAZER = 'LAZER'
    ASSINATURAS = 'ASSINATURAS'
    MORADIA = 'MORADIA'
    CONTAS = 'CONTAS'
    PARCELAS = 'PARCELAS'
    
    #Receitas
    SALARIO = 'SALARIO'
    FREELANCE = 'FREELANCE'
    REEMBOLSO = 'REEMBOLSO'
    VENDA = 'VENDA'
    BONUS = 'BONUS'
    
    #Ambos os tipos (despesas e receitas)
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


class PosicaoInvestimento(Base):
    __tablename__ = "posicoes_investimentos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    ticker = Column(String, nullable=False)               

    valor_investido_brl = Column(Float, nullable=False)     

    quantidade_ativos = Column(Float, nullable=False)       

    cotacao_compra = Column(Float, nullable=False)          

    data_compra = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="investimentos")


   