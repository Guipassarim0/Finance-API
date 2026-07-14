from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.main import oauth2_schema, SECRET_KEY, ALGORITHM
from jwt import decode, DecodeError
from http import HTTPStatus
from app.models import Usuario


# Criando uma dependencia para as rotas terem acesso ao DB.
def pegar_sessao():
    session = SessionLocal()
    try:
        # Yield permite entregar a sesão para a rota.
        # Após a rota terminar, o FastAPI retorna para esta função e executa o finally
        yield session
    
    finally:
        session.close()

def get_current_user(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    
    credentials_exception = HTTPException(
        status_code= HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try: 
       payload = decode(token, SECRET_KEY, algorithms=ALGORITHM)
       subject_email = payload.get("sub")
       if not subject_email:
           raise credentials_exception
    
    except DecodeError:
        raise credentials_exception
    usuario = session.query(Usuario).filter(Usuario.email==subject_email).first()
    if not usuario:
        raise credentials_exception
    
    return usuario