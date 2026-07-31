from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Usuario, Transacao, Categoria, TipoTransacao  
from app.schemas import TransacaoSchema, FiltroRelatorioSchema    
from app.dependencies import pegar_sessao, get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta


transacao_router = APIRouter(prefix="/transacao", tags=["CRUD Transações"])

#Rota de criar transação (receita, despesa), do usuario logado
@transacao_router.post('/criar_transacao')
async def criar_transacao(dados_transacao: TransacaoSchema, current_user: Usuario = Depends(get_current_user),  session: Session = Depends(pegar_sessao)):

    agora = datetime.now()
    data_envio = dados_transacao.data or agora

    '''
    Foi usado o (tzinfo=None) para tratar o conflito de fuso horarios gerado pelo datetime.now(), 
    pois ao comparar um objeto de data aware com um naive o python gera um erro fatal, e o .replace(tzinfo=None)
    faz com que ambas as datas fiquem na mesma "prateleira" para a comparação
    '''
    data_comparacao = data_envio.replace(tzinfo=None)

    limite_passado = agora - timedelta(days=30)
    limite_futuro = datetime(agora.year, 12, 31, 23, 59, 59) 

    
    if data_comparacao < limite_passado:
        raise HTTPException(
            status_code=400,
            detail="Não é permitido registrar transações com mais de 7 dias de atraso."
        )
    
    if data_comparacao > limite_futuro:
        raise HTTPException(
            status_code=400,
            detail=f"Não é permitido agendar transações além do final do ano atual ({agora.year})."
        )

    nova_transacao = Transacao(
        tipo=dados_transacao.tipo,
        categoria=dados_transacao.categoria,
        valor=dados_transacao.valor,
        descricao=dados_transacao.descricao,
        data=data_envio, 
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
@transacao_router.delete('/deletar_transacao')
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
async def resumo_tipos_mensal(mes : int | None = None, ano: int | None = None, current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    hoje = datetime.now()
    ano_busca = hoje.year if ano is None else ano
    mes_busca = hoje.month if mes is None else mes

    if mes_busca > 12 or mes_busca <= 0:
        raise HTTPException(
            status_code=400, 
            detail= "O mês deve ser um número entre 1 e 12."
        )
    
    if ano_busca > hoje.year or ano_busca < hoje.year -1:
        raise HTTPException(
            status_code=400, 
            detail= "Busca permitida apenas para o ano atual ou o ano anterior."
        )

    resumos_tipos = session.query(Transacao.tipo, 
                                  func.sum(Transacao.valor).label('total')).filter(Transacao.usuario_id == current_user.id, 
                                                                                   func.extract('year', Transacao.data) == ano_busca, 
                                                                                   func.extract('month', Transacao.data) == mes_busca).group_by(Transacao.tipo).all()
    
    #func.sum() soma todos os valores do banco de dados, func.extract filtra apenas a data digitada e o .group_by separa os tipos em duas pastas (receitas e despesas) para separas os valores
    #Usei year e month pois o postegres so entende assim, não entende (ano, mes)

    resumo = {
        "RECEITA": 0.0,
        "DESPESA": 0.0,
        "saldo": 0.0,
        "mes": mes_busca,
        "ano": ano_busca
    } 

    for tipo, total in resumos_tipos:

        '''
        Esse for percorre os resultados do banco onde ele devolve ja ordenado ex(transação.receita == 1500), e abaixo ocorrem as somas de saldo e dos tipos 
        com o round para limitar o resultado em 2 casas decimais
        '''

        resumo[tipo.value] = round(total, 2)
    
    resumo["saldo"] = round(resumo["RECEITA"] - resumo["DESPESA"], 2)

    return resumo

@transacao_router.get('/resumo_categorias_mensal')
async def resumo_categorias_mensal(mes : int | None = None, ano : int | None = None, filtros: FiltroRelatorioSchema = Depends(), current_user: Usuario = Depends(get_current_user), session: Session = Depends(pegar_sessao)):

    hoje = datetime.now()
    ano_busca = hoje.year if ano is None else ano
    mes_busca = hoje.month if mes is None else mes

    if mes_busca > 12 or mes_busca <= 0:
        raise HTTPException(
            status_code=400, 
            detail= "O mês deve ser um número entre 1 e 12."
        )
    '''
    Validações de ano e mes não permite que o mes seja menor ou igual a 0, 
    e que o ano seja maior que o atual ou menor que o ano passado
    '''
    if ano_busca > hoje.year or ano_busca < hoje.year -1:
        raise HTTPException(
            status_code=400, 
            detail= "Busca permitida apenas para o ano atual ou o ano anterior."
        )

    '''
    -Validação da data mesmaque a rota de cima o usuario escolhe a data a ser consultada
    -O filtro server para nao deixar que o usuario coloque algo incoerente como (mercado) no tipo de (receita)
    -Não uso o .group_by nessa rota pois o filtro ja separa os tipos e retorna a soma do mes inteiro da categoria desejada
    -O depends() vazio do filtro diz para o fastapi para que ele pegue todos os parametros passados na url
    -O scalar() faz com que o resultado deixe de ser uma lista do banco e devolve o resultado como um numero puro para o pyhton sendo em decimal ou float

    '''

    resumo_categorias = session.query(func.sum(Transacao.valor)).filter(Transacao.usuario_id == current_user.id,
                                                                        Transacao.tipo == filtros.tipo, 
                                                                        Transacao.categoria == filtros.categoria,
                                                                        func.extract('year', Transacao.data) == ano_busca, 
                                                                        func.extract('month', Transacao.data) == mes_busca).scalar()
    
    # Usei year e month pois o postegres so entende assim, não entende (ano, mes)
     
    return {
        "categoria": filtros.categoria.value,
        "mes" : mes_busca,
        "ano" : ano_busca,
        "total" : round(resumo_categorias, 2) if resumo_categorias is not None else 0.0

    }



        

           