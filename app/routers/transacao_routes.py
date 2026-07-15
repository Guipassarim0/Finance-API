from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Usuario, Transacao  
from app.schemas import TransacaoSchema    
from app.dependencies import pegar_sessao, get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

transacao_router = APIRouter(prefix="/transacao", tags=["Transação"])

@transacao_router.post('/criar_transacao')
async def criar_transacao(dados_transacao: TransacaoSchema, current_user: Usuario = Depends(get_current_user),  session: Session = Depends(pegar_sessao)):
    nova_transacao = Transacao(
        tipo=dados_transacao.tipo,
        categoria=dados_transacao.categoria,
        valor=dados_transacao.valor,
        descricao=dados_transacao.descricao,
        data=dados_transacao.data, 
        usuario_id=current_user.id  
        )

    session.add(nova_transacao)
    session.commit()
    session.refresh(nova_transacao)

    return {
        "mensagem": "Transação criada com sucesso!",
        "transacao": {
            "tipo": nova_transacao.tipo,
            "categoria": nova_transacao.categoria,
            "descricao": nova_transacao.descricao,
            "valor": nova_transacao.valor,
            "data": nova_transacao.data,
            "id": nova_transacao.id,
            
        }
    }

