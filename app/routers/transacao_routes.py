from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Usuario, Transacao  
from app.schemas import TransacaoSchema    
from app.dependencies import pegar_sessao, get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime


transacao_router = APIRouter(prefix="/transacao", tags=["CRUD Transações"])

#Rota de criar transação (receita, despesa), do usuario logado
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

#Rota que lista todas as transações feitas pelo usuario logado
@transacao_router.get('/listar_transacoes')
async def listar_transacoes(current_user: Usuario = Depends(get_current_user),  session: Session = Depends(pegar_sessao)):
    
    minhas_transacoes = session.query(Transacao).filter(Transacao.usuario_id==current_user.id).all()

    return [
        {
        "tipo": transacoes.tipo,
        "categoria": transacoes.categoria,
        "valor": transacoes.valor,
        "descricao": transacoes.descricao,
        "data": transacoes.data.strftime("%Y-%m-%d %H:%M:%S")if transacoes.data else None,
        "id": transacoes.id
        } 
        for transacoes in minhas_transacoes
    ]   

#Rota de deletar transações do usuario logado
@transacao_router.delete('/deletar_transação')
async def deletar_transação(id: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    transacao_deletada = session.query(Transacao).filter(Transacao.usuario_id==current_user.id, Transacao.id==id).first()

    if not transacao_deletada:
        raise HTTPException(
            status_code=404,
            detail='Transação não encontrada, ou ja deletada!!'
        )
    
    dados_retorno = {
        "id": transacao_deletada.id,
        "tipo": transacao_deletada.tipo,
        "categoria": transacao_deletada.categoria,
        "valor": transacao_deletada.valor,
        "descricao": transacao_deletada.descricao,
        "data": transacao_deletada.data.strftime("%Y-%m-%d %H:%M:%S") if transacao_deletada.data else None
    }
    
    session.delete(transacao_deletada)
    session.commit()
   
    return {
        "mensagem": f"Transação com id {dados_retorno['id']} deletada com sucesso",
        "transacao": dados_retorno
    }

#Rota de listagem de resumo mensal dos tipos
@transacao_router.get('/resumo_tipos_mensal')
async def resumo_mensal(mes : int, ano: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    hoje = datetime.now()
    ano_busca = ano or hoje.year
    mes_busca = mes or hoje.month

    resumos_tipos = session.query(Transacao.tipo, 
                                  func.sum(Transacao.valor).label('total')).filter(Transacao.usuario_id == current_user.id, 
                                                                                   func.extract('year', Transacao.data) == ano_busca, 
                                                                                   func.extract('month', Transacao.data) == mes_busca).group_by(Transacao.tipo).all()
    
    resumo = {
        "RECEITA": 0.0,
        "DESPESA": 0.0,
        "saldo": 0.0,
        "mes": mes_busca,
        "ano": ano_busca
    } 

    for tipo, total in resumos_tipos:

        resumo[tipo.value] = round(total, 2)

    resumo["saldo"] = round(resumo["RECEITA"] - resumo["DESPESA"], 2)

    return resumo
        

           