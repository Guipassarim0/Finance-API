from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from app.main import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, pwd_context
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import Usuario
from app.schemas import  UsuarioSchema, Token
from app.dependencies import pegar_sessao
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jwt import encode

auth_router = APIRouter(prefix="/auth", tags=["Autenticação"])

@auth_router.post("/criar_conta")
async def criar_conta(usuarioSchema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
   usuario = session.query(Usuario).filter(Usuario.email==usuarioSchema.email).first()
   if usuario:
        raise HTTPException(
            status_code=400, 
            detail="Email do usuario ja cadastrado")
   else:
        hashed_password = pwd_context.hash(usuarioSchema.senha)
        novo_usuario = Usuario(email=usuarioSchema.email, senha=hashed_password, nome= usuarioSchema.nome)
        session.add(novo_usuario)
        session.commit()
        session.refresh(novo_usuario)
        return {
            "email": f"{usuarioSchema.email}", "nome": f"{usuarioSchema.nome}", "id": f"{novo_usuario.id}"}
          

def autenticar_usuario(email: str, senha: str, session: Session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    
    if not pwd_context.verify(senha, usuario.senha):
        return False
    
    return usuario

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

@auth_router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):

     usuario = autenticar_usuario(form_data.username, form_data.password, session)

     if not usuario:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, 
            detail="Email ou Senha Incorreto")

     access_token = create_access_token(
         {"sub": usuario.email}
     )

     return {
         "access_token": access_token,
          "token_type": "Bearer"}

