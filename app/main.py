from fastapi import FastAPI
from pwdlib import PasswordHash

import os
from dotenv import load_dotenv

load_dotenv()
# Criptografia das senhas do DB
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

from fastapi.security import OAuth2PasswordBearer
pwd_context = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

from app.database import engine, Base
from app import models


Base.metadata.create_all(bind=engine)

app = FastAPI()

from app.routers.auth_routes import auth_router
from app.routers.transacao_routes import transacao_router
from app.routers.investimento_routes import investimento_router

app.include_router(auth_router)
app.include_router(transacao_router)
app.include_router(investimento_router)