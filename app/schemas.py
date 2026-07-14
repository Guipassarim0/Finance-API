from pydantic import BaseModel, EmailStr
from decimal import Decimal
from typing import Optional

class UsuarioSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str


    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str