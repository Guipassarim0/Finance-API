from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from decimal import Decimal
from typing import Optional
from datetime import datetime, date
from app.models import TipoTransacao, Categoria 
from fastapi import HTTPException

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# Define o que é permitido em cada tipo de transação
CATEGORIAS_POR_TIPO = {
    TipoTransacao.RECEITA: {
        Categoria.SALARIO,
        Categoria.FREELANCE,
        Categoria.REEMBOLSO,
        Categoria.INVESTIMENTOS,
        Categoria.VENDA,
        Categoria.BONUS,
        Categoria.PRESENTE,  # Pode ser receita
        Categoria.OUTROS     # Pode ser receita
    },
    TipoTransacao.DESPESA: {
        Categoria.MERCADO,
        Categoria.ALIMENTACAO,
        Categoria.TRANSPORTE,
        Categoria.SAUDE,
        Categoria.LAZER,
        Categoria.ASSINATURAS,
        Categoria.MORADIA,
        Categoria.CONTAS,
        Categoria.PARCELAS,
        Categoria.PRESENTE,  # Pode ser despesa 
        Categoria.OUTROS     # Pode ser despesa
    }
}

class TransacaoSchema(BaseModel):
    tipo: TipoTransacao
    categoria: Categoria
    valor: Decimal = Field(gt=0, description="O valor deve ser maior que zero")
    descricao: Optional[str] = None
    data: Optional[date] = None

    @field_validator("tipo", "categoria", mode="before")
    @classmethod
    def transformar_em_maiusculo(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @model_validator(mode="after")
    def validar_categoria_coerente(self):
        tipo_enviado = self.tipo
        categoria_enviada = self.categoria

        permitidas = CATEGORIAS_POR_TIPO.get(tipo_enviado)

        if permitidas is None:
            raise HTTPException(
                status_code=404,
                detail='campo não pode estar vazio'
            )

        if categoria_enviada not in permitidas:
            raise ValueError(
                f"A categoria '{categoria_enviada.value}' não é permitida para o tipo '{tipo_enviado.value}'."
            )
        return self

    class Config:
        from_attributes = True