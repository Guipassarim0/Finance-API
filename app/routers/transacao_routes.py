from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Usuario, Transacao, Categoria, TipoTransacao  
from app.schemas import TransacaoSchema, FiltroRelatorioSchema    
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

#Rota de listagem de resumo mensal dos tipos(receita, despesas)
@transacao_router.get('/resumo_tipos_mensal')
async def resumo_tipos_mensal(mes : int, ano: int, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    hoje = datetime.now()
    ano_busca = ano or hoje.year
    mes_busca = mes or hoje.month

    resumos_tipos = session.query(Transacao.tipo, 
                                  func.sum(Transacao.valor).label('total')).filter(Transacao.usuario_id == current_user.id, 
                                                                                   func.extract('year', Transacao.data) == ano_busca, 
                                                                                   func.extract('month', Transacao.data) == mes_busca).group_by(Transacao.tipo).all()
    
    #func.sum() soma todos os valores do banco de dados, func.extract filtra apenas a data digitada e o .group_by separa os tipos em duas pastas (receitas e despesas) para separas os valores
    #usei year e month pois o postegres so entende assim, não entende (ano, mes)
    
    resumo = {
        "RECEITA": 0.0,
        "DESPESA": 0.0,
        "saldo": 0.0,
        "mes": mes_busca,
        "ano": ano_busca
    } 

    for tipo, total in resumos_tipos:

        '''
        esse for percorre os resultados do banco onde ele devolve ja ordenado ex(transação.receita == 1500), e abaixo ocorrem as somas de saldo e dos tipos 
        com o round para limitar o resultado em 2 casas decimais

        '''

        resumo[tipo.value] = round(total, 2)
    
    resumo["saldo"] = round(resumo["RECEITA"] - resumo["DESPESA"], 2)

    return resumo

@transacao_router.get('/resumo_categorias_mensal')
async def resumo_categorias_mensal(mes : int, ano : int, filtros: FiltroRelatorioSchema = Depends(), current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    hoje = datetime.now()
    ano_busca = ano or hoje.year
    mes_busca = mes or hoje.month

    '''
    -validação da data mesmaque a rota de cima o usuario escolhe a data a ser consultada
    -o filtro server para nao deixar que o usuario coloque algo incoerente como (mercado) no tipo de (receita)
    -nao uso o .group_by nessa rota pois o filtro ja separa os tipos e retorna a soma do mes inteiro da categoria desejada
    -o depends() vazio do filtro diz para o fastapi para que ele pegue todos os parametros passados na url
    -o scalar() faz com que o resultado deixe de ser uma lista do banco e devolve o resultado como um numero puro para o pyhton sendo em decimal ou float

    '''

    resumo_categorias = session.query(func.sum(Transacao.valor)).filter(Transacao.usuario_id == current_user.id,
                                                                        Transacao.tipo == filtros.tipo, 
                                                                        Transacao.categoria == filtros.categoria,
                                                                        func.extract('year', Transacao.data) == ano_busca, 
                                                                        func.extract('month', Transacao.data) == mes_busca).scalar()
    
     #usei year e month pois o postegres so entende assim, não entende (ano, mes)
    
    return {
        "categoria": filtros.categoria.value,
        "mes" : mes_busca,
        "ano" : ano_busca,
        "total" : round(resumo_categorias, 2) if resumo_categorias is not None else 0.0

    }



        

           