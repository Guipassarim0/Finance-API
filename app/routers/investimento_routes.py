from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import pegar_sessao, get_current_user
from app.models import PosicaoInvestimento, Usuario
from app.schemas import InvestimentoCreateSchema, InvestimentoResponseSchema, ResumoCarteiraSchema
from app.services.finance_service import FinanceService
from typing import List

investimento_router = APIRouter(prefix="/investimentos", tags=["Investimentos"])
# Essa é a rota de comprar investimentos
@investimento_router.post("/comprar", response_model=InvestimentoResponseSchema, status_code=status.HTTP_201_CREATED, summary="Registrar compra de um ativo/moeda")
async def comprar_investimento(dados: InvestimentoCreateSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(get_current_user)):
    """
    Registra a compra de um ativo (ex: USD, EUR, PETR4, VALE3).
    A cotação é consultada em tempo real e a quantidade comprada é calculada automaticamente.
    """
    # Chama o serviço financeiro para consultar o valor da cotação em tempo real do ativo/moeda, e o await espera a resposta da api externa
    cotacao = await FinanceService.obter_cotacao(dados.ticker)

    # Se a cotação retornar None ou o usuario digitar um ativo nao catalogado, o ativo não existe
    if cotacao is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ativo '{dados.ticker}' não foi encontrado ou está indisponível no mercado."
        )

    # Calcula a quantidade de ativos/moedas adquiridos
    quantidade_comprada = dados.valor_investido / cotacao

    novo_investimento = PosicaoInvestimento(
        usuario_id=usuario.id,
        ticker=dados.ticker.upper(),
        valor_investido_brl=dados.valor_investido,
        cotacao_compra=cotacao,
        quantidade_ativos=quantidade_comprada
    )

    session.add(novo_investimento)
    session.commit()
    session.refresh(novo_investimento)

    return novo_investimento

# Essa é a rota de historico de investimentos comprados
@investimento_router.get("/historico", response_model=List[InvestimentoResponseSchema], summary="Listar todo o histórico de compras do usuário")
async def obter_historico_compras(session: Session = Depends(pegar_sessao),usuario: Usuario = Depends(get_current_user)):
    """
    Retorna apenas a lista de transações de compra cadastradas no banco de dados.
    Esta rota é ultra rápida pois não consulta APIs de mercado externas, ela consulta apenas os dados do banco de dados.
    """
    transacoes = session.query(PosicaoInvestimento).filter(PosicaoInvestimento.usuario_id == usuario.id).all()

    return transacoes

# Essa é a rota que agrupa os investimentos e devolve o resumo deles
@investimento_router.get("/resumo", response_model=ResumoCarteiraSchema, summary="Obter patrimônio total e acumulado agrupado por ativo")
async def obter_resumo_carteira(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(get_current_user)):
    """
    Agrupa os ativos, calcula a soma das quantidades, busca a cotação 
    de HOJE no mercado e devolve o valor patrimonial total recalculado.
    """
    transacoes = session.query(PosicaoInvestimento).filter(PosicaoInvestimento.usuario_id == usuario.id).all()


    # Essa validação verifica se o usuario nao tem nenhum investimento registrado, caso ele não tenha o metodo get retorna tudo zerado
    if not transacoes:
        return ResumoCarteiraSchema(
            patrimonio_total_atual_brl=0.0,
            total_investido_historico_brl=0.0,
            ativos_agrupados=[]
        )


    agrupado = {}
    total_investido_geral = 0.0

    for item in transacoes:
        ticker = item.ticker.upper()

        if ticker not in agrupado:
            agrupado[ticker] = {
                "total_qtd": 0.0,
                "total_investido": 0.0
            }

        agrupado[ticker]["total_qtd"] += item.quantidade_ativos
        agrupado[ticker]["total_investido"] += item.valor_investido_brl
        total_investido_geral += item.valor_investido_brl

    '''
    Essa é a logica de soma dos ativos ela começa criando um dicionario vazio. 
    Depois ela percorre cada compra pelo for, se o ativo nao estiver no dicionario ela adiciona com os valores zerados.
    Apos isso ela acumula as quantidades e valores em R$ para agrupar todas as compras daquele mesmo ativo.
    E por fim mantem o somatorio de total_investido_geral de todo o histórico do usuário
    '''


    ativos_consolidados = []
    patrimonio_total_atual = 0.0

    for ticker, dados in agrupado.items():
        cotacao_atual = await FinanceService.obter_cotacao(ticker)
        
        if cotacao_atual is None:
            cotacao_atual = dados["total_investido"] / dados["total_qtd"]
            # Se a API financeira falhar ou o ativo sumir do mercado, calcula o preço médio histórico para a aplicação não quebrar.

        valor_atual_brl = dados["total_qtd"] * cotacao_atual
        lucro_prejuizo = valor_atual_brl - dados["total_investido"]

        '''
        Aqui acontece os calculos com base na cotação atual 
        A primeira é do valor atual que seria a quantidade acumulada do ativo pelo preço atual de mercado
        A segunda calcula a rentabilidade, onde ela faz o valor atual ja calculado menos o total investido historicamente
        '''

        patrimonio_total_atual += valor_atual_brl

        ativos_consolidados.append({
            "ticker": ticker,
            "total_investido_brl": round(dados["total_investido"], 2),
            "total_quantidade": round(dados["total_qtd"], 2),
            "cotacao_atual": round(cotacao_atual, 2),
            "valor_atual_brl": round(valor_atual_brl, 2),
            "lucro_prejuizo_brl": round(lucro_prejuizo, 2)
        })

    return ResumoCarteiraSchema(
        patrimonio_total_atual_brl=round(patrimonio_total_atual, 2),
        total_investido_historico_brl=round(total_investido_geral, 2),
        ativos_agrupados=ativos_consolidados
    )


