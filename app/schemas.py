from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from app.models import TipoTransacao, Categoria 

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
    data: Optional[datetime] = None

    @field_validator("tipo", "categoria", mode="before")
    @classmethod
    def transformar_em_maiusculo(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    @model_validator(mode="after")
    def validar_categoria_coerente(self):
        permitidas = CATEGORIAS_POR_TIPO[self.tipo]

        if self.categoria not in permitidas:
            raise ValueError(
                f"A categoria '{self.categoria.value}' não é permitida para o tipo '{self.tipo.value}'."
            )

        return self

    class Config:
        from_attributes = True

class FiltroRelatorioSchema(TransacaoSchema):

    valor: Decimal | None = None

class InvestimentoCreateSchema(BaseModel):
    ticker: str = Field(..., example="USD", description="Ticker do ativo (ex: USD, EUR, PETR4)")
    valor_investido: float = Field(..., gt=0, example=1500.0, description="Valor em R$ a ser investido")

class InvestimentoResponseSchema(BaseModel):
    id: int
    ticker: str
    valor_investido_brl: float
    quantidade_ativos: float
    cotacao_compra: float

    @field_validator("valor_investido_brl", "quantidade_ativos", "cotacao_compra", mode="after")
    @classmethod
    def arredondar_floats(cls, v: float) -> float:
        if v is not None:
            return round(v, 2)
        return v

    class Config:
        from_attributes = True


class AtivoConsolidadoSchema(BaseModel):
    ticker: str
    total_investido_brl: float
    total_quantidade: float
    cotacao_atual: float
    valor_atual_brl: float
    lucro_prejuizo_brl: float

class ResumoCarteiraSchema(BaseModel):
    patrimonio_total_atual_brl: float
    total_investido_historico_brl: float
    ativos_agrupados: List[AtivoConsolidadoSchema]
